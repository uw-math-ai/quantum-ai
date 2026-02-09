from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import gymnasium as gym
import numpy as np
from gymnasium import spaces


@dataclass
class LineWorldConfig:
    min_pos: int = -5
    max_pos: int = 5
    max_steps: int = 30


class LineWorldEnv(gym.Env[np.int64, int]):
    """A tiny 1D environment where the agent walks left/right to reach a boundary."""

    metadata = {"render_modes": ["ansi"], "render_fps": 4}

    def __init__(self, config: Optional[LineWorldConfig] = None, render_mode: Optional[str] = None) -> None:
        self.config = config or LineWorldConfig()
        self.render_mode = render_mode

        self.action_space = spaces.Discrete(2)  # 0 = left, 1 = right
        self.observation_space = spaces.Discrete(self.config.max_pos - self.config.min_pos + 1)

        self._pos = 0
        self._steps = 0

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None):
        super().reset(seed=seed)
        self._pos = 0
        self._steps = 0
        obs = self._to_obs()
        info: dict[str, Any] = {}
        return obs, info

    def step(self, action: int):
        self._steps += 1
        if action == 0:
            self._pos -= 1
        else:
            self._pos += 1

        terminated = self._pos <= self.config.min_pos or self._pos >= self.config.max_pos
        truncated = self._steps >= self.config.max_steps

        reward = 0.0
        if self._pos <= self.config.min_pos:
            reward = -1.0
        elif self._pos >= self.config.max_pos:
            reward = 1.0

        obs = self._to_obs()
        info: dict[str, Any] = {}
        return obs, reward, terminated, truncated, info

    def render(self):
        if self.render_mode != "ansi":
            return None
        line = ["."] * (self.config.max_pos - self.config.min_pos + 1)
        idx = self._pos - self.config.min_pos
        if 0 <= idx < len(line):
            line[idx] = "A"
        return "".join(line)

    def _to_obs(self) -> np.int64:
        return np.int64(self._pos - self.config.min_pos)
