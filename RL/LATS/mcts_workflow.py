"""
MCTS (Monte Carlo Tree Search) Workflow for Quantum Circuit Generation.

Uses llama-index Workflows API to implement tree search-based exploration
of circuit action spaces with the CircuitBuilderEnv.

This is a modern alternative to deprecated LATS, providing more control
over the search algorithm while leveraging the Workflows event-driven architecture.
"""

import sys
import json
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add parent directories to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for CopilotWrapper

from llama_index.core.workflow import Workflow, Context, step
from workflows.events import Event, StartEvent, StopEvent

from CopilotWrapper import CopilotWrapper
from RL.envs.CircuitBuilderEnv import CircuitBuilderEnv, CircuitBuilderConfig
import stim
import mqt.qecc.codes as qecc


# ============================================================================
# Environment Snapshot
# ============================================================================

class EnvSnapshot:
    """Lightweight snapshot of all mutable CircuitBuilderEnv state."""

    __slots__ = (
        "circ",
        "steps_taken",
        "last_ft_score",
        "proportion_stab_preserved",
        "last_stabilizer_count",
        "target_stab_count",
    )

    def __init__(
        self,
        circ: stim.Circuit,
        steps_taken: int,
        last_ft_score: float,
        proportion_stab_preserved: float,
        last_stabilizer_count: int,
        target_stab_count: int,
    ) -> None:
        self.circ = circ
        self.steps_taken = steps_taken
        self.last_ft_score = last_ft_score
        self.proportion_stab_preserved = proportion_stab_preserved
        self.last_stabilizer_count = last_stabilizer_count
        self.target_stab_count = target_stab_count


# ============================================================================
# Events  (plain Pydantic BaseModel subclasses — no @dataclass)
# ============================================================================

class SelectionEvent(Event):
    """Triggered to start/continue tree selection from root."""
    node_id: str


class ExpansionEvent(Event):
    """Triggered when a leaf node has been selected for expansion."""
    node_id: str


class SimulationEvent(Event):
    """Triggered when a new child node is ready for rollout."""
    node_id: str


class BackupEvent(Event):
    """Triggered after simulation to propagate reward up the tree."""
    node_id: str
    value_delta: float = 0.0


# ============================================================================
# MCTS Tree Node
# ============================================================================

class TreeNode:
    """A node in the MCTS tree."""

    def __init__(
        self,
        node_id: str,
        parent_id: Optional[str] = None,
        action: Optional[int] = None,            # integer action that produced this node
        snapshot: Optional["EnvSnapshot"] = None, # env state at this node
        depth: int = 0,
        untried_actions: Optional[List[int]] = None,
    ):
        self.node_id = node_id
        self.parent_id = parent_id
        self.action = action
        self.snapshot = snapshot
        self.depth = depth
        self.untried_actions: List[int] = untried_actions or []

        self.visits = 0
        self.value = 0.0
        self.children: Dict[int, str] = {}   # action_int -> child_node_id
        self.is_terminal = False

    def ucb(self, parent_visits: int, c: float = 1.414) -> float:
        """UCT formula: Q/n + c * sqrt(ln(N) / n) where N = parent visits."""
        if self.visits == 0:
            return float('inf')
        return self.value / self.visits + c * math.sqrt(math.log(max(1, parent_visits)) / self.visits)

    def update(self, reward: float) -> None:
        """Update node statistics with rollout reward."""
        self.visits += 1
        self.value += reward


def _append_measure(action_ints: List[int], env: CircuitBuilderEnv) -> None:
    """
    Ensure the measure/terminate action (\"M\") is always the last entry in
    *action_ints*, appending it if it isn't already present.  This guarantees
    every node has at least one terminal branch to explore.
    """
    m_int = env.action_to_int("M")
    if m_int in action_ints:
        action_ints.remove(m_int)
    action_ints.append(m_int)


# ============================================================================
# MCTS Workflow
# ============================================================================

class QuantumMCTSWorkflow(Workflow):
    """
    MCTS-based workflow for quantum circuit generation.

    Searches the space of circuit actions using Monte Carlo tree search,
    balancing exploration vs exploitation (UCT) to find circuits that maximise
    stabiliser preservation and fault tolerance.

    Each tree node stores a lightweight EnvSnapshot (circuit + scalar fields).
    Restoring a node is a single stim.Circuit.copy() plus six scalar assignments —
    much cheaper than replaying the full action path from root.
    """

    def __init__(
        self,
        env: CircuitBuilderEnv,
        llm: CopilotWrapper,
        max_iterations: int = 100,
        top_k: int = 5,
        c_puct: float = 1.414,
        verbose: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.env = env
        self.llm = llm
        self.max_iterations = max_iterations
        self.c_puct = c_puct
        self.top_k = top_k
        self.verbose = verbose

        # Tree stored on the instance; shared and mutated across all steps.
        self.tree: Dict[str, TreeNode] = {}
        self.root_id = "root"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _llm_ranked_actions(
        self,
        circuit_str: str,
        step_details: Optional[Dict[str, Any]] = None,
    ) -> List[int]:
        """
        Ask the LLM to rank the top-k most promising next actions given the
        current circuit state and the step details from the most recent env.step().
        Returns a list of at most `top_k` valid integer action indices ordered
        best-first, with the "M" (measure/terminate) action always appended last.
        Falls back to a random sample on any parse or validation failure.
        """
        one_qubit = ", ".join(sorted(self.env.config.one_qubit_gates))
        two_qubit = ", ".join(sorted(self.env.config.two_qubit_gates))
        stabs = ", ".join(self.env.stab_code.stabs_as_pauli_strings())
        n_data = self.env.config.num_data_qubits
        flag_start = self.env.total_qubits - self.env.config.num_flag_qubits
        flag_end = self.env.total_qubits - 1

        # Format step feedback if available
        if step_details:
            preserved = step_details.get("stabilizers_preserved", "?")  
            total = len(self.env.stab_code.stabs_as_pauli_strings())
            proportion = step_details.get("proportion_preserved", 0.0)
            ft = step_details.get("ft_score", 0.0)
            stab_map = step_details.get("stabilizers_preservation", {})
            stab_status = ", ".join(
                f"{s}={'✓' if v else '✗'}" for s, v in stab_map.items()
            )
            feedback = (
                f"\nCurrent status after last gate:\n"
                f"  Stabilizers preserved: {preserved}/{total} ({proportion:.0%}) [{stab_status}]\n"
                f"  Fault-tolerance score: {ft:.4f}\n"
            )
        else:
            feedback = ""

        prompt = (
            f"You are designing a fault-tolerant quantum circuit using Stim.\n\n"
            f"Current circuit:\n{circuit_str if circuit_str.strip() else '<empty>'}\n"
            f"{feedback}\n"
            f"Goal: Preserve ALL stabilizers [{stabs}] and achieve fault tolerance.\n"
            f"Data qubits: 0\u2013{n_data - 1}\n"
            f"Flag qubits: {flag_start}\u2013{flag_end}\n"
            f"One-qubit gates: {one_qubit}\n"
            f"Two-qubit gates: {two_qubit}\n\n"
            f"Select the {self.top_k} most promising NEXT operations, ordered best-first.\n"
            f"Reply with ONLY a JSON array, e.g.: [[\"H\", 0], [\"CNOT\", 0, 3], [\"M\"]]\n\n"
            f"Rules:\n"
            f"- One-qubit gate: [\"GATE\", qubit]\n"
            f"- Two-qubit gate: [\"GATE\", control, target]  (control \u2260 target)\n"
            f"- Measure all flag qubits and terminate: [\"M\"]\n"
            f"- Use only the gates and qubit indices listed above."
        )

        try:
            response = await self.llm.acomplete(prompt)
            text = response.text.strip()
            # Locate the outermost JSON array
            start = text.find("[")
            end = text.rfind("]") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON array in response")
            parsed = json.loads(text[start:end])

            action_ints: List[int] = []
            for item in parsed:
                if not isinstance(item, list) or len(item) == 0:
                    continue
                try:
                    if item[0] == "M":
                        action_int = self.env.action_to_int("M")
                    elif len(item) == 2:
                        action_int = self.env.action_to_int((str(item[0]), int(item[1])))
                    elif len(item) == 3:
                        action_int = self.env.action_to_int(
                            (str(item[0]), int(item[1]), int(item[2]))
                        )
                    else:
                        continue
                except (ValueError, KeyError):
                    continue  # skip invalid gate/qubit combos
                if 0 <= action_int < self.env.action_space.n:
                    action_ints.append(action_int)
                if len(action_ints) >= self.top_k:
                    break

            if action_ints:
                if self.verbose:
                    print(
                        f"  [LLM] top-{len(action_ints)} actions: "
                        f"{[self.env.int_to_action(a) for a in action_ints]}"
                    )
                _append_measure(action_ints, self.env)
                return action_ints

        except Exception as exc:
            if self.verbose:
                print(f"  [LLM] parse error ({exc}); falling back to random sample")

        # Fallback: random sample of top_k actions
        pool = list(range(self.env.action_space.n))
        random.shuffle(pool)
        fallback = pool[: self.top_k]
        _append_measure(fallback, self.env)
        return fallback

    def _snapshot_env(self) -> "EnvSnapshot":
        """Capture all mutable env state into a lightweight snapshot."""
        return EnvSnapshot(
            circ=self.env.circ.copy(),
            steps_taken=self.env.steps_taken,
            last_ft_score=self.env.last_ft_score,
            proportion_stab_preserved=self.env.proportion_stab_preserved,
            last_stabilizer_count=self.env.last_stabilizer_count,
            target_stab_count=self.env.target_stab_count,
        )

    def _restore_snapshot(self, snapshot: EnvSnapshot) -> None:
        """Restore env to a previously captured snapshot (copy circ to keep snapshot pristine)."""
        self.env.circ = snapshot.circ.copy()
        self.env.steps_taken = snapshot.steps_taken
        self.env.last_ft_score = snapshot.last_ft_score
        self.env.proportion_stab_preserved = snapshot.proportion_stab_preserved
        self.env.last_stabilizer_count = snapshot.last_stabilizer_count
        self.env.target_stab_count = snapshot.target_stab_count

    def _node_id(self, parent_id: str, action_int: int) -> str:
        """Stable, collision-free child node ID."""
        return f"{parent_id}_a{action_int}"

    def _get_best_path(self) -> List[Any]:
        """
        Walk the tree greedily by most-visited child and return the sequence
        of human-readable actions (via env.int_to_action).
        """
        path: List[Any] = []
        node_id: Optional[str] = self.root_id
        while node_id is not None:
            node = self.tree[node_id]
            best_child_id: Optional[str] = None
            best_visits = -1
            for child_id in node.children.values():
                child = self.tree[child_id]
                if child.visits > best_visits:
                    best_visits = child.visits
                    best_child_id = child_id
            if best_child_id is None:
                break
            child = self.tree[best_child_id]
            if child.action is not None:
                path.append(self.env.int_to_action(child.action))
            node_id = best_child_id
        return path

    # ------------------------------------------------------------------
    # Workflow steps
    # ------------------------------------------------------------------

    @step
    async def initialize_search(self, ctx: Context, _ev: StartEvent) -> SelectionEvent:
        """Initialise the search tree with a root node and reset the environment."""
        if self.verbose:
            print("Initialising MCTS search…")

        self.env.reset()
        root_snapshot = self._snapshot_env()
        root_untried = await self._llm_ranked_actions(str(self.env.circ), step_details=None)
        root = TreeNode(
            node_id=self.root_id,
            parent_id=None,
            action=None,
            snapshot=root_snapshot,
            depth=0,
            untried_actions=root_untried,
        )
        self.tree[self.root_id] = root
        await ctx.set("iteration", 0)
        return SelectionEvent(node_id=self.root_id)

    @step
    async def select_node(self, _ctx: Context, ev: SelectionEvent) -> ExpansionEvent:
        """
        Descend the tree using UCT until we find a node that still has
        untried actions (leaf) or is terminal.
        """
        node_id = ev.node_id
        node = self.tree[node_id]

        while (
            len(node.untried_actions) == 0
            and len(node.children) > 0
            and not node.is_terminal
        ):
            best_child_id: Optional[str] = None
            best_ucb = -float("inf")
            for child_id in node.children.values():
                child = self.tree[child_id]
                ucb_val = child.ucb(parent_visits=node.visits, c=self.c_puct)
                if ucb_val > best_ucb:
                    best_ucb = ucb_val
                    best_child_id = child_id

            if best_child_id is None:
                break

            node_id = best_child_id
            node = self.tree[node_id]

        return ExpansionEvent(node_id=node_id)

    @step
    async def expand_node(self, _ctx: Context, ev: ExpansionEvent) -> SimulationEvent:
        """
        Pop the highest-priority LLM-ranked untried action from the selected
        node, create a child, restore the environment to the child state, then
        ask the LLM for the child's own top-k candidate actions.
        One new child is created per iteration so the tree grows gradually.
        """
        node_id = ev.node_id
        node = self.tree[node_id]

        # If nothing left to expand or terminal, simulate from this node itself.
        if node.is_terminal or len(node.untried_actions) == 0:
            return SimulationEvent(node_id=node_id)

        # Pop best-ranked untried action (LLM ordered best-first)
        action_int = node.untried_actions.pop(0)
        child_id = self._node_id(node_id, action_int)

        # Restore env to parent's snapshot, step one action to reach child state.
        self._restore_snapshot(node.snapshot)
        _, _, child_done, child_truncated, child_details = self.env.step(action_int)
        child_is_terminal = child_done or child_truncated

        # Snapshot the child state immediately after the step.
        child_snapshot = self._snapshot_env()

        # Ask LLM for top-k candidates from child's circuit (skip if terminal).
        if child_is_terminal:
            child_untried: List[int] = []
        else:
            child_untried = await self._llm_ranked_actions(
                str(self.env.circ), step_details=child_details
            )

        child = TreeNode(
            node_id=child_id,
            parent_id=node_id,
            action=action_int,
            snapshot=child_snapshot,
            depth=node.depth + 1,
            untried_actions=child_untried,
        )
        child.is_terminal = child_is_terminal
        self.tree[child_id] = child
        node.children[action_int] = child_id

        return SimulationEvent(node_id=child_id)

    @step
    async def simulate(self, ctx: Context, ev: SimulationEvent) -> BackupEvent:
        """
        Restore the environment to the node's snapshot, then perform a random
        rollout and return the cumulative reward.
        """
        node_id = ev.node_id
        node = self.tree[node_id]

        if node.is_terminal or node.snapshot is None:
            return BackupEvent(node_id=node_id, value_delta=0.0)
        self._restore_snapshot(node.snapshot)

        rollout_reward = 0.0
        remaining = self.env.config.max_gates - self.env.steps_taken
        for _ in range(max(remaining, 1)):
            action = self.env.action_space.sample()
            _, reward, done, truncated, _ = self.env.step(action)
            rollout_reward += reward
            if done or truncated:
                break

        if self.verbose:
            iteration = await ctx.get("iteration", default=0)
            print(
                f"  [iter {iteration}] node={node_id} "
                f"depth={node.depth} rollout={rollout_reward:.3f}"
            )

        return BackupEvent(node_id=node_id, value_delta=rollout_reward)

    @step
    async def backup(
        self, ctx: Context, ev: BackupEvent
    ) -> Union[SelectionEvent, StopEvent]:
        """Backpropagate the rollout reward up to the root; loop or terminate."""
        node_id: Optional[str] = ev.node_id
        while node_id is not None:
            node = self.tree[node_id]
            node.update(ev.value_delta)
            node_id = node.parent_id

        iteration: int = await ctx.get("iteration", default=0)
        iteration += 1
        await ctx.set("iteration", iteration)

        if iteration >= self.max_iterations:
            best_path = self._get_best_path()
            if self.verbose:
                print(f"\nMCTS complete after {iteration} iterations.")
                print(f"Best path ({len(best_path)} steps): {best_path}")
            return StopEvent(result=best_path)

        return SelectionEvent(node_id=self.root_id)


# ============================================================================
# Example Usage
# ============================================================================

async def run_mcts_example():
    """Example usage of the MCTS workflow."""

    stabilizers = ["XXX", "ZZI", "IZZ"]
    code = qecc.StabilizerCode(generators=stabilizers, distance=1, n=3)

    env_config = CircuitBuilderConfig(
        max_gates=32,
        num_data_qubits=3,
        num_flag_qubits=2,
    )
    env = CircuitBuilderEnv(code, config=env_config, render_mode="string")

    llm = CopilotWrapper(
        model="ollama:ministral-3b",
        temperature=0.5,
        timeout=300,
    )

    workflow = QuantumMCTSWorkflow(
        env=env,
        llm=llm,
        max_iterations=20,
        top_k=5,
        verbose=True,
    )

    print("Starting MCTS workflow…")
    result = await workflow.run()

    print("\n" + "=" * 60)
    print("MCTS Search Results")
    print("=" * 60)
    print(f"Best path found: {result}")
    print(f"Number of steps: {len(result) if result else 0}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_mcts_example())
