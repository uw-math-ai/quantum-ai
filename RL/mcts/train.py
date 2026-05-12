from __future__ import annotations

from .alphazero_agent import AlphaZeroAgent, IterationStats
from .config import AlphaZeroConfig


def run_training(cfg: AlphaZeroConfig, num_iterations: int, seed_base: int = 0) -> list[IterationStats]:
    agent = AlphaZeroAgent(cfg)
    try:
        return agent.train_iterations(num_iterations=num_iterations, seed_base=seed_base)
    finally:
        agent.close()
