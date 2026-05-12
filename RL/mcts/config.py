from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import torch


EnvFactory = Callable[[], Any]
ModelFactory = Callable[[], torch.nn.Module]


@dataclass
class MCTSConfig:
    num_simulations: int = 64
    c_puct: float = 1.5
    gamma: float = 0.99
    temperature: float = 1.0


@dataclass
class TrainConfig:
    episodes_per_iteration: int = 16
    gradient_steps_per_iteration: int = 32
    batch_size: int = 64
    learning_rate: float = 3e-4
    value_coef: float = 1.0


@dataclass
class ParallelConfig:
    num_cpu_workers: int = 4
    learner_gpu_id: int = 0
    inference_gpu_ids: list[int] = field(default_factory=list)
    worker_queue_size: int = 8
    sync_timeout_s: float = 120.0
    collect_timeout_s: float = 900.0

    def resolved_inference_gpu_ids(self) -> list[int]:
        if self.inference_gpu_ids:
            return self.inference_gpu_ids
        n = torch.cuda.device_count()
        if n <= 1:
            return [self.learner_gpu_id] if n == 1 else []
        return [i for i in range(n) if i != self.learner_gpu_id]


@dataclass
class AlphaZeroConfig:
    env_factory: EnvFactory
    model_factory: ModelFactory
    mcts: MCTSConfig = field(default_factory=MCTSConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    parallel: ParallelConfig = field(default_factory=ParallelConfig)
