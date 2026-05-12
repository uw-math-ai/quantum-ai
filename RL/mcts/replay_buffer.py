from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random
from typing import Any

import numpy as np
import torch


@dataclass(frozen=True)
class Sample:
    obs: Any
    pi: np.ndarray
    z: float


class ReplayBuffer:
    def __init__(self, capacity: int = 100_000) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._data: deque[Sample] = deque(maxlen=capacity)

    def __len__(self) -> int:
        return len(self._data)

    def add(self, sample: Sample) -> None:
        self._data.append(sample)

    def add_many(self, samples: list[Sample]) -> None:
        self._data.extend(samples)

    def sample_batch(self, batch_size: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if len(self._data) < batch_size:
            raise ValueError("Not enough samples in replay buffer")

        batch = random.sample(list(self._data), batch_size)
        obs = torch.as_tensor(np.stack([np.asarray(x.obs) for x in batch]), dtype=torch.float32)
        pi = torch.as_tensor(np.stack([x.pi for x in batch]), dtype=torch.float32)
        z = torch.as_tensor([x.z for x in batch], dtype=torch.float32)
        return obs, pi, z
