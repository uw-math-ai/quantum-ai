"""
Step-based reward scoring for CircuitBuilderEnv.

Reward design:
- Per-step reward: 0 (no intermediate reward or penalty)
- Terminal reward (on done=True):
    - Only counts stabilizers satisfied BEYOND the initial baseline
    - base = max(new_satisfied_at_any_step) / total_stabilizers
    - reward = satisfaction_bonus * base
    - If ALL stabilizers satisfied at final step: + success_bonus
    - If fully solved: + efficiency_bonus * (1 - steps_used / max_steps)

Key insight: The initial |0...0> state already satisfies all Z-type stabilizers
for free. Without baseline subtraction, the agent learns to immediately measure
and collect ~50% reward without building any circuit.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple

import stim

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from check_stabilizers import check_stabilizers


class StepRewardModel:
    """Reward model for step-based circuit building."""

    def __init__(
        self,
        satisfaction_bonus: float = 10.0,
        success_bonus: float = 5.0,
        efficiency_bonus: float = 2.0,
        max_steps: int = 64,
    ) -> None:
        self.satisfaction_bonus = satisfaction_bonus
        self.success_bonus = success_bonus
        self.efficiency_bonus = efficiency_bonus
        self.max_steps = max_steps

        self._max_new_satisfied: int = 0
        self._steps_used: int = 0
        self._initial_satisfied: int | None = None

    def reset(self) -> None:
        """Call at the start of each episode."""
        self._max_new_satisfied = 0
        self._steps_used = 0
        self._initial_satisfied = None

    def _count_satisfied(self, circuit_str: str, target_stabilizers: List[str]) -> int:
        stab_results = check_stabilizers(circuit_str, target_stabilizers)
        return sum(stab_results.values())

    def score_step(
        self,
        circuit: stim.Circuit,
        target_stabilizers: List[str],
        prev_satisfied: int,
        done: bool,
    ) -> Tuple[float, Dict]:
        """Score a single step.

        Returns 0 reward on intermediate steps.
        Returns terminal reward on done=True based on NEW satisfactions
        beyond the initial baseline.
        """
        self._steps_used += 1
        total_stabilizers = len(target_stabilizers)

        details: Dict[str, object] = {
            "done": done,
            "steps_used": self._steps_used,
        }

        circuit_str = str(circuit)
        try:
            current_satisfied = self._count_satisfied(circuit_str, target_stabilizers)
        except Exception:
            if done:
                return -5.0, {**details, "error": "stabilizer_check_failed"}
            return 0.0, {**details, "error": "stabilizer_check_failed"}

        # Track baseline on first call
        if self._initial_satisfied is None:
            self._initial_satisfied = current_satisfied

        # Only count satisfactions beyond baseline
        new_satisfied = max(0, current_satisfied - self._initial_satisfied)
        self._max_new_satisfied = max(self._max_new_satisfied, new_satisfied)

        details["current_satisfied"] = current_satisfied
        details["initial_satisfied"] = self._initial_satisfied
        details["new_satisfied"] = new_satisfied
        details["max_new_satisfied"] = self._max_new_satisfied
        details["total_stabilizers"] = total_stabilizers

        # Intermediate step: no reward
        if not done:
            return 0.0, details

        # === Terminal reward ===
        reward = 0.0

        # Base reward: proportional to best NEW satisfaction achieved
        satisfaction_ratio = self._max_new_satisfied / total_stabilizers
        reward += self.satisfaction_bonus * satisfaction_ratio

        # Bonus for complete solution at the final step
        fully_solved = (current_satisfied == total_stabilizers)
        if fully_solved:
            reward += self.success_bonus
            efficiency = 1.0 - (self._steps_used / self.max_steps)
            reward += self.efficiency_bonus * max(0.0, efficiency)

        details["satisfaction_ratio"] = satisfaction_ratio
        details["fully_solved"] = fully_solved
        details["reward"] = reward

        return reward, details