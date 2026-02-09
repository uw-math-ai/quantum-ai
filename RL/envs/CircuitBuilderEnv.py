from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Literal

import gymnasium as gym
import numpy as np
import numpy.typing as npt
from gymnasium import spaces

import stim

@dataclass
class CircuitBuilderConfig:
    one_qubit_gates: set[str] = field(default_factory=lambda: {"H", "X", "Y", "Z", "S"})
    two_qubit_gates: set[str] = field(default_factory=lambda: {"CNOT"})
    max_gates: int = 128
    num_qubits: int = 16

class CircuitBuilderEnv(gym.Env[npt.NDArray[np.integer[Any]], int]):
    """Environment for building a stabilizer circuit"""

    metadata = {"render_modes": ["string", "diagram"]}

    def __init__(self, stabs: list[str], config: CircuitBuilderConfig = CircuitBuilderConfig(), render_mode: Optional[Literal["string", "diagram"]] = None) -> None:
        self.config = config
        self.render_mode = render_mode
        if any([len(stab) > config.num_qubits for stab in stabs]):
            raise ValueError("One or more stabilizers have more qubits than the configuration allows.")
        self.stabs = stabs
        self.gate_map = {gate: i for i, gate in enumerate(list(config.one_qubit_gates) + list(config.two_qubit_gates))}
        self.action_space = spaces.Discrete(
            len(self.config.one_qubit_gates) * self.config.num_qubits +
            len(self.config.two_qubit_gates) * self.config.num_qubits**2 +
            self.config.num_qubits)  # terminal measurement actions for k in [1, num_qubits]
        tableau_rows = 2 * self.config.num_qubits
        tableau_cols = 2 * self.config.num_qubits + 1
        self.observation_space = spaces.MultiBinary((tableau_rows, tableau_cols))
        self.steps_taken = 0

    def _init_circuit(self, randomize: bool = False) -> stim.Circuit:
        if randomize:
            return stim.Tableau.random(self.config.num_qubits).to_circuit()
        else:
            return stim.Tableau(self.config.num_qubits).to_circuit()

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None):
        super().reset(seed=seed)
        self.circ = self._init_circuit(options.get("randomize", False) if options else False)
            
        self.steps_taken = 0
        return self._to_obs()

    def step(self, action: int):
        done = False
        reward = 0

        action_decoded = self.int_to_action(action)
        if len(action_decoded) == 2 and action_decoded[0] == "M":
            _, k = action_decoded
            start = self.config.num_qubits - k
            self.flag_qubits = list(range(start, self.config.num_qubits))
            self.circ.append("M", self.flag_qubits)
            done = True
        elif len(action_decoded) == 2:
            # one-qubit gate
            gate, target = action_decoded
            self.steps_taken += 1
            self.circ.append(gate, [target]) # type: ignore[arg-type]
        else:
            # two-qubit gate
            gate, control, target = action_decoded
            self.steps_taken += 1
            self.circ.append(gate, [control, target]) # type: ignore[arg-type]
        
        if self.steps_taken >= self.config.max_gates:
            done = True
            # probably fail because no measurement

        if done:
            # TODO: calculate terminal condition
            pass
        else:
            # TODO: calculate intermediate reward
            self.circ
            pass

        return self._to_obs(), reward, done, False, {}

    def action_to_int(self, action: tuple[str, int] | tuple[str, int, int] | tuple[Literal["M"], int]) -> int:
        """
        Converts a human-readable action into an integer index for the action space.

        :param action: (two-qubit gate, control qubit, target qubit), (one-qubit gate, target qubit), or ("M", k)
        :type action: tuple[str, int] | tuple[str, int, int] | tuple[Literal["M"], int]
        :return: Integer index corresponding to the action
        :rtype: int
        """
        if isinstance(action, tuple) and len(action) == 2:
            gate, target = action
            if gate == "M":
                k = target
                if k < 1 or k > self.config.num_qubits:
                    raise ValueError("Measurement size k is out of bounds.")
                base = (
                    len(self.config.one_qubit_gates) * self.config.num_qubits +
                    len(self.config.two_qubit_gates) * self.config.num_qubits**2
                )
                return base + (k - 1)
            gate_idx = self.gate_map.get(gate)
            if gate_idx is None or gate not in self.config.one_qubit_gates:
                raise ValueError("Invalid one-qubit gate.")
            return gate_idx * self.config.num_qubits + target
        elif isinstance(action, tuple) and len(action) == 3:
            gate, control, target = action
            gate_idx = self.gate_map.get(gate)
            if gate_idx is None or gate not in self.config.two_qubit_gates:
                raise ValueError("Invalid two-qubit gate.")
            return (len(self.config.one_qubit_gates) * self.config.num_qubits) + (gate_idx - len(self.config.one_qubit_gates)) * self.config.num_qubits**2 + control * self.config.num_qubits + target
        else:
            raise ValueError("Invalid action format.")
        
    def int_to_action(self, action_int: int) -> tuple[str, int] | tuple[str, int, int] | tuple[Literal["M"], int]:
        """
        Converts an integer index from the action space back into a human-readable action.

        :param action_int: Integer index corresponding to the action
        :type action_int: int
        :return: (two-qubit gate, control qubit, target qubit), (one-qubit gate, target qubit), or ("M", k)
        :rtype: tuple[str, int] | tuple[str, int, int] | tuple[Literal["M"], int]
        """
        if action_int < 0 or action_int >= self.action_space.n:
            raise ValueError("Action integer out of bounds.")

        one_qubit_limit = len(self.config.one_qubit_gates) * self.config.num_qubits
        two_qubit_limit = one_qubit_limit + len(self.config.two_qubit_gates) * self.config.num_qubits**2

        if action_int < one_qubit_limit:
            gate_idx = action_int // self.config.num_qubits
            target = action_int % self.config.num_qubits
            gate = list(self.config.one_qubit_gates)[gate_idx]
            return (gate, target)
        if action_int < two_qubit_limit:
            two_qubit_offset = one_qubit_limit
            gate_idx = (action_int - two_qubit_offset) // self.config.num_qubits**2 + len(self.config.one_qubit_gates)
            control_target_offset = (action_int - two_qubit_offset) % self.config.num_qubits**2
            control = control_target_offset // self.config.num_qubits
            target = control_target_offset % self.config.num_qubits
            gate = list(self.config.two_qubit_gates)[gate_idx - len(self.config.one_qubit_gates)]
            return (gate, control, target)

        k = (action_int - two_qubit_limit) + 1
        return ("M", k)

    def render(self):
        if self.render_mode == "string":
            return str(self.circ)
        elif self.render_mode == "diagram":
            return self.circ.diagram()

    def _to_obs(self) -> npt.NDArray[np.int8]:
        xs, zs, xs2, zs2, px, pz = stim.Tableau.from_circuit(self.circ, ignore_measurement=True).to_numpy()
        top = np.concatenate([xs, zs, px[:,None]], axis=1)
        bottom = np.concatenate([xs2, zs2, pz[:, None]], axis=1)
        return np.concatenate([top, bottom], axis=0).astype(np.int8)
    

if __name__ == "__main__":
    stabs = [
        "XZZXI",
        "IXZZX",
        "XIXZZ",
        "ZXIXZ",
        "ZZXIX",
    ]
    env = CircuitBuilderEnv(stabs, config = CircuitBuilderConfig(max_gates=64, num_qubits=5), render_mode="string")
    obs = env.reset(options={"randomize": False })
    print(env.circ.num_qubits)
    print(env.render())
    for action_int in range(env.action_space.n):
        action = env.int_to_action(action_int)
        print(f"Action int: {action_int} -> Action: {action}")
        assert env.action_to_int(action) == action_int, f"Round-trip conversion failed for action int {action_int}"

