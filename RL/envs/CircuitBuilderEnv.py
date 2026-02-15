from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Literal

import sys

import gymnasium as gym
import numpy as np
import numpy.typing as npt
from gymnasium import spaces

import stim
import mqt.qecc.codes as qecc

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from tools.check_error_propagation import ft_score
from tools.check_stabilizers import check_stabilizers

@dataclass
class CircuitBuilderRewards:
    failure_penalty: float = -1.0
    success_reward: float = 1.0
    step_penalty: float = -0.01
    ft_score_p: float = 1.0
    ft_score_scale: float = 1.0
    dst_score_scale: float = 1.0

@dataclass
class CircuitBuilderConfig:
    one_qubit_gates: set[str] = field(default_factory=lambda: {"H", "X", "Y", "Z", "S"})
    two_qubit_gates: set[str] = field(default_factory=lambda: {"CNOT"})
    max_gates: int = 128
    num_data_qubits: int = 32
    num_flag_qubits: int = 2
    rewards: CircuitBuilderRewards = field(default_factory=CircuitBuilderRewards)

class CircuitBuilderEnv(gym.Env[npt.NDArray[np.integer[Any]], int]):
    """Environment for building a stabilizer circuit"""

    metadata = {"render_modes": ["string", "diagram"]}

    def __init__(self, stab_code: qecc.StabilizerCode, config: CircuitBuilderConfig = CircuitBuilderConfig(), render_mode: Optional[Literal["string", "diagram"]] = None) -> None:
        self.config = config
        self.render_mode = render_mode
        if any([len(stab) > config.num_data_qubits for stab in stab_code.stabs_as_pauli_strings()]):
            raise ValueError("One or more stabilizers have more qubits than the configuration allows.")
        if config.num_flag_qubits < 0:
            raise ValueError("Number of flag qubits must be non-negative.")
        if config.num_data_qubits < 1:
            raise ValueError("Number of data qubits must be at least 1.")
        self.stab_code = stab_code
        padded_stabs = [stab.ljust(config.num_data_qubits, 'I') for stab in stab_code.stabs_as_pauli_strings()]
        self.stab_tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(stab) for stab in padded_stabs],
            allow_underconstrained=True
        )
        self.total_qubits = self.config.num_data_qubits + self.config.num_flag_qubits
        self.data_qubits = list(range(self.config.num_data_qubits))
        self.data_qubit_idx = np.array(self.data_qubits, dtype=int)
        if self.config.num_flag_qubits == 0:
            self.flag_qubits = []
        else:
            start = self.total_qubits - self.config.num_flag_qubits
            self.flag_qubits = list(range(start, self.total_qubits))
        self.gate_map = {gate: i for i, gate in enumerate(list(config.one_qubit_gates) + list(config.two_qubit_gates))}
        self.action_space = spaces.Discrete(
            len(self.config.one_qubit_gates) * self.total_qubits +
            len(self.config.two_qubit_gates) * self.total_qubits**2 +
            1)  # terminal measurement action for all flag qubits
        tableau_rows = 2 * self.total_qubits
        tableau_cols = 2 * self.total_qubits + 1
        self.observation_space = spaces.MultiBinary((tableau_rows, tableau_cols))

    def _init_circuit(self, randomize: bool = False) -> stim.Circuit:
        if randomize:
            return stim.Tableau.random(self.total_qubits).to_circuit()
        else:
            return stim.Tableau(self.total_qubits).to_circuit()

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None):
        super().reset(seed=seed)
        self.circ = self._init_circuit(options.get("randomize", False) if options else False)
        self.steps_taken = 0
        self.last_ft_score = 0.
        self.last_dst = 0.
        return self._to_obs()

    def step(self, action: int):
        done = False
        reward = 0.0
        details = dict()

        invalid_action = action < 0 or action >= self.action_space.n
        if not invalid_action:
            action_decoded = self.int_to_action(action)
            if action_decoded == "M":
                if self.flag_qubits:
                    self.circ.append("M", self.flag_qubits) # type: ignore[arg-type]
                done = True
            elif len(action_decoded) == 2:
                # one-qubit gate
                gate, target = action_decoded
                self.steps_taken += 1
                self.circ.append(gate, [target]) # type: ignore[arg-type]
            else:
                # two-qubit gate
                gate, control, target = action_decoded
                if control == target:
                    invalid_action = True
                    details["invalid_action"] = "Control and target qubits cannot be the same for a two-qubit gate."
                else:
                    self.steps_taken += 1
                    self.circ.append(gate, [control, target]) # type: ignore[arg-type]
            
            if self.steps_taken > self.config.max_gates:
                invalid_action = True
                details["invalid_action"] = f"Exceeded maximum number of gates: {self.steps_taken} > {self.config.max_gates}"
        else:
            details["invalid_action"] = f"Action integer is out of bounds: {action} not in [0, {self.action_space.n})"

        if invalid_action:
            reward += self.config.rewards.failure_penalty
            done = True
        else:
            reward += self.config.rewards.step_penalty

            ft = ft_score(str(self.circ), list(range(self.config.num_data_qubits)),
                          self.flag_qubits,
                          p=self.config.rewards.ft_score_p,
                          d = self.stab_code.distance if self.stab_code.distance is not None else 1)
            dst = _tableau_distance(
                self.stab_tableau,
                stim.Tableau.from_circuit(self.circ, ignore_measurement=True),
                self.data_qubit_idx,
            )

            reward += (ft - self.last_ft_score) * self.config.rewards.ft_score_scale # higher ft_score is better
            reward += (self.last_dst - dst) * self.config.rewards.dst_score_scale
            self.last_ft_score = ft
            self.last_dst = dst
            details["ft_score"] = ft
            details["distance"] = dst
            if done:
                stabilizers = check_stabilizers(str(self.circ), self.stab_code.stabs_as_pauli_strings())
                if not all(stabilizers.values()):
                    reward += self.config.rewards.failure_penalty
                else:
                    reward += self.config.rewards.success_reward
                
                details["stabilizers_preservation"] = stabilizers
        
        return self._to_obs(), reward, done, False, details

    def action_to_int(self, action: tuple[str, int] | tuple[str, int, int] | Literal["M"]) -> int:
        """
        Converts a human-readable action into an integer index for the action space.

        :param action: (two-qubit gate, control qubit, target qubit), (one-qubit gate, target qubit), or "M"
        :type action: tuple[str, int] | tuple[str, int, int] | Literal["M"]
        :return: Integer index corresponding to the action
        :rtype: int
        """
        if action == "M":
            return (
                len(self.config.one_qubit_gates) * self.total_qubits +
                len(self.config.two_qubit_gates) * self.total_qubits**2
            )
        if isinstance(action, tuple) and len(action) == 2:
            gate, target = action
            gate_idx = self.gate_map.get(gate)
            if gate_idx is None or gate not in self.config.one_qubit_gates:
                raise ValueError("Invalid one-qubit gate.")
            return gate_idx * self.total_qubits + target
        elif isinstance(action, tuple) and len(action) == 3:
            gate, control, target = action
            gate_idx = self.gate_map.get(gate)
            if gate_idx is None or gate not in self.config.two_qubit_gates:
                raise ValueError("Invalid two-qubit gate.")
            return (len(self.config.one_qubit_gates) * self.total_qubits) + (gate_idx - len(self.config.one_qubit_gates)) * self.total_qubits**2 + control * self.total_qubits + target
        else:
            raise ValueError("Invalid action format.")
        
    def int_to_action(self, action_int: int) -> tuple[str, int] | tuple[str, int, int] | Literal["M"]:
        """
        Converts an integer index from the action space back into a human-readable action.

        :param action_int: Integer index corresponding to the action
        :type action_int: int
        :return: (two-qubit gate, control qubit, target qubit), (one-qubit gate, target qubit), or "M"
        :rtype: tuple[str, int] | tuple[str, int, int] | Literal["M"]
        """
        if action_int < 0 or action_int >= self.action_space.n:
            raise ValueError("Action integer out of bounds.")

        one_qubit_limit = len(self.config.one_qubit_gates) * self.total_qubits
        two_qubit_limit = one_qubit_limit + len(self.config.two_qubit_gates) * self.total_qubits**2

        if action_int < one_qubit_limit:
            gate_idx = action_int // self.total_qubits
            target = action_int % self.total_qubits
            gate = list(self.config.one_qubit_gates)[gate_idx]
            return (gate, target)
        if action_int < two_qubit_limit:
            two_qubit_offset = one_qubit_limit
            gate_idx = (action_int - two_qubit_offset) // self.total_qubits**2 + len(self.config.one_qubit_gates)
            control_target_offset = (action_int - two_qubit_offset) % self.total_qubits**2
            control = control_target_offset // self.total_qubits
            target = control_target_offset % self.total_qubits
            gate = list(self.config.two_qubit_gates)[gate_idx - len(self.config.one_qubit_gates)]
            return (gate, control, target)

        return "M"

    def render(self):
        if self.render_mode == "string":
            return str(self.circ)
        elif self.render_mode == "diagram":
            return self.circ.diagram()

    def _to_obs(self) -> npt.NDArray[np.int8]:
        return _tableau_to_np(stim.Tableau.from_circuit(self.circ, ignore_measurement=True))
    
def _tableau_to_np(tableau: stim.Tableau) -> npt.NDArray[np.int8]:
    xs, zs, xs2, zs2, px, pz = tableau.to_numpy()
    top = np.concatenate([xs, zs, px[:,None]], axis=1)
    bottom = np.concatenate([xs2, zs2, pz[:, None]], axis=1)
    return np.concatenate([top, bottom], axis=0).astype(np.int8)

def _tableau_to_np_masked(tableau: stim.Tableau, data_qubits: npt.NDArray[np.int64]) -> npt.NDArray[np.int8]:
    xs, zs, xs2, zs2, px, pz = tableau.to_numpy()
    xs = xs[np.ix_(data_qubits, data_qubits)]
    zs = zs[np.ix_(data_qubits, data_qubits)]
    xs2 = xs2[np.ix_(data_qubits, data_qubits)]
    zs2 = zs2[np.ix_(data_qubits, data_qubits)]
    px = px[data_qubits]
    pz = pz[data_qubits]
    top = np.concatenate([xs, zs, px[:, None]], axis=1)
    bottom = np.concatenate([xs2, zs2, pz[:, None]], axis=1)
    return np.concatenate([top, bottom], axis=0).astype(np.int8)

def _tableau_distance(target: stim.Tableau, source: stim.Tableau, data_qubits: npt.NDArray[np.int64]) -> float:
    """Compute the distance between two tableaus over data qubits only."""
    target_np = _tableau_to_np_masked(target, data_qubits)
    source_np = _tableau_to_np_masked(source, data_qubits)
    diff_norm = np.linalg.norm(target_np - source_np)
    denom = np.linalg.norm(target_np) + np.linalg.norm(source_np)
    if denom == 0.0:
        return 0.0
    return float(diff_norm / denom)

if __name__ == "__main__":
    stabs = [
        "XZZXI",
        "IXZZX",
        "XIXZZ",
        "ZXIXZ",
    ]

    code = qecc.StabilizerCode(generators=stabs, distance=3, n=5)

    env = CircuitBuilderEnv(code, config = CircuitBuilderConfig(max_gates=64, num_data_qubits=5, num_flag_qubits=2), render_mode="string")
    obs = env.reset(options={"randomize": False })
    print(env.circ.num_qubits)
    print(env.render())
    for action_int in range(env.action_space.n):
        action = env.int_to_action(action_int)
        print(f"Action int: {action_int} -> Action: {action}")
        assert env.action_to_int(action) == action_int, f"Round-trip conversion failed for action int {action_int}"