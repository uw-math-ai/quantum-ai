from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Literal

import sys
import copy

import gymnasium as gym
import numpy as np
import numpy.typing as npt
from gymnasium import spaces

import stim

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))


@dataclass
class BackwardStatePrepRewards:
    failure_penalty: float = -100.0
    success_reward: float = 100.0
    step_penalty: float = -0.1
    # Reward scale for incremental improvement in fidelity to target state
    fidelity_scale: float = 1.0


@dataclass
class BackwardStatePrepConfig:
    one_qubit_gates: list[str] = field(default_factory=lambda: ["H", "X", "Y", "Z", "S"])
    two_qubit_gates: list[str] = field(default_factory=lambda: ["CNOT"])
    # Similarity metric used for the complementary distance reward: 'jaccard' (default) or 'hamming'
    distance_metric: Literal["jaccard", "hamming"] = "jaccard"
    rewards: BackwardStatePrepRewards = field(default_factory=BackwardStatePrepRewards)


class BackwardStatePrepEnv(gym.Env[npt.NDArray[np.int8], int]):
    """
    Gym environment for backward state preparation.

    The agent starts from a target stabilizer state and applies inverse gates
    in an attempt to disentangle it back to the |0...0> computational basis
    state. Equivalently, reading the agent's chosen circuit in reverse yields
    a preparation circuit for the target state.

    Observation: Binary tableau representation of the current circuit's action
    on the all-zeros state, encoded as a (n x (2n+1)) numpy array of int8.
    Columns are [X-part | Z-part | phase], one row per Z-stabilizer generator.

    Action space: Discrete - one-qubit gates on any qubit, two-qubit gates on
    ordered control/target pairs with control != target.
    """

    metadata = {"render_modes": ["string", "diagram"]}

    def __init__(
        self,
        circuit: stim.Circuit,
        config: BackwardStatePrepConfig = BackwardStatePrepConfig(),
        render_mode: Optional[Literal["string", "diagram"]] = None,
    ) -> None:
        """
        :param target_stabilizers: Pauli strings defining the target stabilizer state
            (e.g. ["XX", "ZZ"] for a 2-qubit Bell state).
        :param config: Environment configuration.
        :param render_mode: Render mode for human-readable output.
        """
        self.target_circuit = circuit
        self.config = config
        self.num_qubits = circuit.num_qubits
        self.render_mode = render_mode
        self.max_gates = sum(len(inst.targets_copy()) for inst in circuit)

        # Canonical target vector for |0...0>: check matrix is [0|I], sign is 0
        # Already in RREF, so no elimination needed.
        n = self.num_qubits
        target_check = np.concatenate(
            [np.zeros((n, n), dtype=np.int8), np.eye(n, dtype=np.int8)], axis=1
        )
        target_sign = np.zeros(n, dtype=np.int8)
        self.target_vec = np.concatenate([target_check.flatten(), target_sign])

        n = self.num_qubits
        self.gate_map: dict[str, int] = {
            gate: i
            for i, gate in enumerate(config.one_qubit_gates + config.two_qubit_gates)
        }

        # Action space: 1q gates × n qubits  +  2q gates × n*(n-1) ordered pairs
        self.num_two_qubit_pairs = n * (n - 1)
        self.action_space = spaces.Discrete(
            len(config.one_qubit_gates) * n
            + len(config.two_qubit_gates) * self.num_two_qubit_pairs
        )

        # Observation: binary z-stabilizers tableau  shape (n, 2n+1)
        # Includes phase column so the agent can distinguish +P from -P stabilizers
        tableau_rows = n
        tableau_cols = 2 * n + 1
        self.observation_space = spaces.MultiBinary((tableau_rows, tableau_cols))

    # ------------------------------------------------------------------
    # Core gym API
    # ------------------------------------------------------------------

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict[str, Any]] = None,
    ):
        super().reset(seed=seed)
        # Begin with the target state's preparation circuit (empty inverse = start at target)
        self.curr_circ = self.target_circuit.copy()
        self.steps_taken = 0
        self.appended_gates = []
        obs = self._to_obs()
        self.last_fidelity = self._compute_fidelity(obs)
        return obs, {}

    def step(self, action: int):
        done = False
        truncated = False
        reward = 0.0
        info: dict[str, Any] = {}

        # ---- validate action ----
        parsed_action = self.int_to_action(action)
        if len(parsed_action) == 2:
            gate, target = parsed_action
            self.curr_circ.append(gate, [target])
            self.appended_gates.append((gate, [target]))
        elif len(parsed_action) == 3:
            gate, control, target = parsed_action
            self.curr_circ.append(gate, [control, target])
            self.appended_gates.append((gate, [control, target]))
        self.steps_taken += 1

        # ---- compute reward ----
        obs = self._to_obs()  # always recompute from current circuit
        fidelity = self._compute_fidelity(obs)
        reward += self.config.rewards.fidelity_scale * (fidelity - self.last_fidelity)
        self.last_fidelity = fidelity
        reward += self.config.rewards.step_penalty
        info["fidelity"] = fidelity

        if fidelity == 1.0:
            reward += self.config.rewards.success_reward
            done = True
            info["success"] = True
        elif self.steps_taken >= self.max_gates:
            reward += self.config.rewards.failure_penalty
            done = True
            info["success"] = False

        return obs, reward, done, truncated, info

    def render(self):
        if self.curr_circ.num_qubits == 0:
            return "<Empty circuit>"
        if self.render_mode == "string":
            return str(self.curr_circ)
        elif self.render_mode == "diagram":
            return self.curr_circ.diagram()

    # ------------------------------------------------------------------
    # Action encoding / decoding
    # ------------------------------------------------------------------

    def action_to_int(
        self,
        action: tuple[str, int] | tuple[str, int, int],
    ) -> int:
        """Convert a human-readable action to an integer index.

        Encoding (qubit-major):
          1q: target * num_1q_gates + gate_idx
                    2q: one_qubit_limit + pair_idx(control, target) * num_2q_gates + gate_idx
                            where pair_idx skips control == target.
        """
        n = self.num_qubits
        num_1q = len(self.config.one_qubit_gates)
        num_2q = len(self.config.two_qubit_gates)
        one_qubit_limit = num_1q * n

        if isinstance(action, tuple) and len(action) == 2:
            gate, target = action
            if gate not in self.config.one_qubit_gates:
                raise ValueError(f"Unknown one-qubit gate: {gate!r}")
            gate_idx = self.gate_map[gate]
            return target * num_1q + gate_idx

        if isinstance(action, tuple) and len(action) == 3:
            gate, control, target = action
            if gate not in self.config.two_qubit_gates:
                raise ValueError(f"Unknown two-qubit gate: {gate!r}")
            if control == target:
                raise ValueError("Invalid two-qubit action: control and target must differ.")
            gate_idx = self.gate_map[gate] - len(self.config.one_qubit_gates)
            pair_idx = self._pair_to_index(control, target)
            return one_qubit_limit + pair_idx * num_2q + gate_idx

        raise ValueError(f"Invalid action format: {action!r}")

    def int_to_action(
        self, action_int: int
    ) -> tuple[str, int] | tuple[str, int, int]:
        """Convert an integer index back to a human-readable action."""
        n = self.num_qubits
        num_1q = len(self.config.one_qubit_gates)
        num_2q = len(self.config.two_qubit_gates)
        one_qubit_limit = num_1q * n

        if action_int < 0 or action_int >= self.action_space.n:
            raise ValueError(f"Action integer {action_int} out of bounds.")

        if action_int < one_qubit_limit:
            target   = action_int // num_1q
            gate_idx = action_int % num_1q
            gate = list(self.config.one_qubit_gates)[gate_idx]
            return (gate, target)

        # Two-qubit gate
        offset   = action_int - one_qubit_limit
        pair_idx = offset // num_2q
        gate_idx = offset % num_2q
        control, target = self._index_to_pair(pair_idx)
        gate = list(self.config.two_qubit_gates)[gate_idx]
        return (gate, control, target)

    def _pair_to_index(self, control: int, target: int) -> int:
        """Map an ordered (control, target) pair with control != target to [0, n*(n-1))."""
        n = self.num_qubits
        if not (0 <= control < n and 0 <= target < n):
            raise ValueError(
                f"Qubit indices out of bounds for n={n}: control={control}, target={target}"
            )
        if control == target:
            raise ValueError("Invalid two-qubit pair: control and target must differ.")

        # Row-major over control, skipping the diagonal entry in each row.
        return control * (n - 1) + (target if target < control else target - 1)

    def _index_to_pair(self, pair_idx: int) -> tuple[int, int]:
        """Inverse mapping of _pair_to_index for pair_idx in [0, n*(n-1))."""
        n = self.num_qubits
        max_pairs = n * (n - 1)
        if pair_idx < 0 or pair_idx >= max_pairs:
            raise ValueError(f"Two-qubit pair index {pair_idx} out of bounds [0, {max_pairs}).")

        control = pair_idx // (n - 1)
        rem = pair_idx % (n - 1)
        target = rem if rem < control else rem + 1
        return control, target

    def get_state_preparation_circuit(self) -> stim.Circuit:
        """Return the current circuit that prepares the target state from |0...0>."""
        prep_circ = stim.Circuit()
        for gate, qubits in reversed(self.appended_gates):
            if gate in self.config.one_qubit_gates:
                prep_circ.append(gate, qubits)
            elif gate in self.config.two_qubit_gates:
                prep_circ.append(gate, qubits)
        return prep_circ

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def get_mcts_state(self) -> dict[str, Any]:
        """Return a lightweight snapshot used by MCTS search workers."""
        return {
            "curr_circ": self.curr_circ.copy(),
            "steps_taken": int(self.steps_taken),
            "appended_gates": copy.deepcopy(self.appended_gates),
            "last_fidelity": float(self.last_fidelity),
        }

    def set_mcts_state(self, state: dict[str, Any]) -> None:
        """Restore snapshot produced by get_mcts_state()."""
        self.curr_circ = state["curr_circ"].copy()
        self.steps_taken = int(state["steps_taken"])
        self.appended_gates = copy.deepcopy(state["appended_gates"])
        self.last_fidelity = float(state["last_fidelity"])

    def _compute_fidelity(self, obs) -> float:
        """
        Complementary distance between the current circuit's stabilizer state and
        |0...0>, following Zen et al. (arXiv:2402.17761).

        1. Extract Z-stabilizer rows (xs2, zs2, pz) from the current tableau.
        2. Row-reduce [xs2 | zs2] over GF(2), propagating the sign.
        3. Flatten and append the sign to form a binary vector.
        4. Compare with the pre-computed target vector via Jaccard or Hamming.

        Returns a value in [0, 1] where 1 means the state equals |0...0>.
        """
        n = self.num_qubits
        xs2  = obs[:, :n]
        zs2  = obs[:, n:2 * n]
        pz   = obs[:, 2 * n]

        canon_check, canon_sign = _gf2_rref(
            np.concatenate([xs2, zs2], axis=1), pz
        )
        current_vec = np.concatenate([canon_check.flatten(), canon_sign])

        if self.config.distance_metric == "hamming":
            return _hamming(current_vec, self.target_vec)
        return _jaccard(current_vec, self.target_vec)
        

    def _to_obs(self) -> npt.NDArray[np.int8]:
        """Encode the current circuit state as a binary tableau numpy array."""
        n = self.num_qubits
        circ_copy = self.curr_circ.copy()
        # Ensure the tableau spans all n qubits even for an empty circuit
        circ_copy.append("H", [n - 1])
        circ_copy.append("H", [n - 1])
        tableau = stim.Tableau.from_circuit(circ_copy, ignore_measurement=True)
        return _tableau_to_np(tableau)


# ------------------------------------------------------------------
# Complementary distance helpers  (Zen et al., arXiv:2402.17761)
# ------------------------------------------------------------------

def _gf2_rref(
    check: npt.NDArray[np.int8], sign: npt.NDArray[np.int8]
) -> tuple[npt.NDArray[np.int8], npt.NDArray[np.int8]]:
    """
    Reduced row echelon form of a GF(2) check matrix.
    Row operations are propagated to the sign vector.

    :param check: (n, 2n) binary check matrix [X-part | Z-part]
    :param sign:  (n,) binary phase vector (0 = +1, 1 = -1)
    :return: (canon_check, canon_sign) in RREF
    """
    mat  = check.copy().astype(np.int8)
    sgn  = sign.copy().astype(np.int8)
    n_rows, n_cols = mat.shape
    pivot_row = 0
    for col in range(n_cols):
        # find first row >= pivot_row with a 1 in this column
        rows_with_one = np.where(mat[pivot_row:, col] == 1)[0]
        if rows_with_one.size == 0:
            continue
        found = rows_with_one[0] + pivot_row
        # swap
        mat[[pivot_row, found]] = mat[[found, pivot_row]]
        sgn[[pivot_row, found]] = sgn[[found, pivot_row]]
        # eliminate all other rows
        others = np.where(mat[:, col] == 1)[0]
        others = others[others != pivot_row]
        mat[others] = (mat[others] + mat[pivot_row]) % 2
        sgn[others] = (sgn[others] + sgn[pivot_row]) % 2
        pivot_row += 1
        if pivot_row >= n_rows:
            break
    return mat, sgn


def _jaccard(v1: npt.NDArray, v2: npt.NDArray) -> float:
    """Jaccard similarity (intersection / union) of two binary vectors."""
    intersection = int(np.logical_and(v1, v2).sum())
    union        = int(np.logical_or(v1, v2).sum())
    return intersection / union if union > 0 else 1.0


def _hamming(v1: npt.NDArray, v2: npt.NDArray) -> float:
    """Hamming similarity (fraction of matching bits) of two binary vectors."""
    return float(np.sum(v1 == v2)) / len(v1)


# ------------------------------------------------------------------
# Tableau utility
# ------------------------------------------------------------------

def _tableau_to_np(tableau: stim.Tableau) -> npt.NDArray[np.int8]:
    _, _, xs2, zs2, _, pz = tableau.to_numpy()
    bottom = np.concatenate([xs2, zs2, pz[:, None]], axis=1)
    return bottom.astype(np.int8)


# ------------------------------------------------------------------
# Quick smoke-test
# ------------------------------------------------------------------

if __name__ == "__main__":
    # 2-qubit Bell state stabilizers: XX, ZZ
    target_stabs = [stim.PauliString(s) for s in ["XX", "ZZ"]]
    circ = stim.Tableau.from_stabilizers(target_stabs, allow_underconstrained=True).to_circuit()
    env = BackwardStatePrepEnv(circ, render_mode="string")

    obsv, info = env.reset()
    print(f"Initial obs shape: {obsv.shape}; obs:\n{obsv}")

    obsv, reward, done, truncated, info = env.step(env.action_to_int(("CNOT", 0, 1)))
    print(f"After CNOT(0,1): reward={reward:.3f}, fidelity={info.get('fidelity', '?'):.3f}")

    obsv, reward, done, truncated, info = env.step(env.action_to_int(("H", 0)))
    print(f"After H(0): reward={reward:.3f}, fidelity={info.get('fidelity', '?'):.3f}")


    print(obsv)

    print(env.render())

    # Round-trip action encoding
    print("\nRound-trip action encoding check:")
    for i in range(env.action_space.n):
        a = env.int_to_action(i)
        print(a)
        assert env.action_to_int(a) == i, f"Round-trip failed for action int {i}"
    print("All OK.")
