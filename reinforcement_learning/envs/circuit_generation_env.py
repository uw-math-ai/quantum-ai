"""
Minimal environment for Agent A (circuit generation).

- reset() -> returns stabilizers for a new episode
- step(circuit_str) -> returns (reward, details)
- evaluate_batch(circuits, stabilizers) -> batch rewards
"""

import os
import sys
from typing import List, Dict, Tuple, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reward"))

from prompt_loader import PromptLoader
from stim_optimizer import RewardComputer


class CircuitGenerationEnv:
    def __init__(self, jsonl_path: str, batch_size: int = 32):
        self.loader = PromptLoader(jsonl_path)
        self.rewarder = RewardComputer()
        self.batch_size = batch_size
        self.current_prompt = None

    def reset(self) -> List[str]:
        self.current_prompt = self.loader.get_random_prompt()
        return self.current_prompt["input_stabilizers"]

    def step(self, circuit_str: str) -> Tuple[float, Dict]:
        if not self.current_prompt:
            raise ValueError("Call reset() before step().")
        stabilizers = self.current_prompt["input_stabilizers"]
        rewards, details = self.rewarder.batch_compute_rewards_agent_a(
            [circuit_str],
            [stabilizers],
        )
        return rewards[0], details[0]

    def get_batch(self, batch_size: Optional[int] = None) -> List[Dict]:
        size = batch_size or self.batch_size
        return self.loader.get_batch(size)

    def evaluate_batch(
        self,
        circuit_strs: List[str],
        stabilizer_sets: List[List[str]],
    ) -> Tuple[List[float], List[Dict]]:
        return self.rewarder.batch_compute_rewards_agent_a(circuit_strs, stabilizer_sets)


if __name__ == "__main__":
    jsonl = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "circuit_permute.jsonl")
    )
    # -- Basic interaction test --
    # env = CircuitGenerationEnv(jsonl)
    # stabs = env.reset()
    # print("Stabilizers:", stabs)
    # reward, details = env.step("H 0\nCX 0 1\nCX 1 2\n")
    # print("Reward:", reward)
    # print("Details:", details)

    # -- Batch evaluation test --
    env = CircuitGenerationEnv(jsonl)
    batch = env.get_batch(batch_size=5)
    batch_stabs = [item["input_stabilizers"] for item in batch]
    batch_circuits = [item["output_circuit"] for item in batch]
    batch_rewards, batch_details = env.evaluate_batch(batch_circuits, batch_stabs)
    print("Batch rewards:", batch_rewards)
    max_scores = [1.0 + 10.0 * len(stabs) for stabs in batch_stabs]
    print("Max possible scores:", max_scores)
