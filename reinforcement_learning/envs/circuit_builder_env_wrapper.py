"""
Wrapper that samples stabilizer prompts and exposes CircuitBuilderEnv.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Add paths for CircuitBuilderEnv (in RL/envs)
ROOT_DIR = Path(__file__).resolve().parents[2]
RL_ENVS_DIR = ROOT_DIR / "RL" / "envs"
sys.path.insert(0, str(RL_ENVS_DIR))

from CircuitBuilderEnv import CircuitBuilderEnv, CircuitBuilderConfig  # noqa: E402

# Add path for PromptLoader
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
sys.path.insert(0, str(DATA_DIR))

from prompt_loader import PromptLoader  # noqa: E402


class CircuitBuilderEnvWrapper:
    """Sample stabilizers from dataset and run step-based CircuitBuilderEnv."""

    metadata = {}

    def __init__(
        self,
        jsonl_path: str,
        config: CircuitBuilderConfig,
        render_mode: Optional[str] = None,
    ) -> None:
        self.loader = PromptLoader(jsonl_path)
        self.config = config
        self.render_mode = render_mode
        self.current_prompt: Optional[Dict[str, Any]] = None

        # Pre-filter using PromptLoader's built-in filter
        self.valid_indices = self.loader.filter_by_num_qubits(
            max_qubits=self.config.num_qubits
        )

        if not self.valid_indices:
            stats = self.loader.get_statistics()
            raise ValueError(
                f"No stabilizer set fits num_qubits={self.config.num_qubits}. "
                f"Qubit distribution in dataset: {stats['qubit_distribution']}. "
                f"Increase config.num_qubits or filter the dataset."
            )

        # Dummy env to expose spaces before first reset
        dummy_stabs = ["I" * self.config.num_qubits]
        self.env = CircuitBuilderEnv(dummy_stabs, config=self.config, render_mode=render_mode)
        self.action_space = self.env.action_space
        self.observation_space = self.env.observation_space

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, Dict[str, Any]]:
        # Sample from pre-filtered valid indices
        idx = random.choice(self.valid_indices)
        self.current_prompt = self.loader.get_prompt(idx)
        stabs = self.current_prompt["input_stabilizers"]

        # Pad stabilizers to num_qubits if shorter
        padded = [s.ljust(self.config.num_qubits, "I") for s in stabs]

        self.env = CircuitBuilderEnv(padded, config=self.config, render_mode=self.render_mode)
        obs = self.env.reset(seed=seed, options=options)
        return obs, {"stabilizers": stabs}

    def step(self, action):
        return self.env.step(action)

    def render(self):
        return self.env.render()

    def close(self):
        if hasattr(self.env, "close"):
            self.env.close()