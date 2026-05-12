from __future__ import annotations

from dataclasses import dataclass
import queue
from typing import Any

import torch

from .config import AlphaZeroConfig
from .replay_buffer import ReplayBuffer, Sample
from .worker import WorkerHandle, start_workers, stop_workers


@dataclass
class IterationStats:
    iteration: int
    collected_samples: int
    replay_size: int
    loss_policy: float
    loss_value: float
    model_version: int


class AlphaZeroAgent:
    def __init__(self, cfg: AlphaZeroConfig, replay_capacity: int = 100_000) -> None:
        self.cfg = cfg

        self.learner_model = cfg.model_factory()
        self.device = self._resolve_learner_device(cfg.parallel.learner_gpu_id)
        self.learner_model.to(self.device)
        self.optimizer = torch.optim.Adam(self.learner_model.parameters(), lr=cfg.train.learning_rate)

        self.replay = ReplayBuffer(capacity=replay_capacity)
        self.workers: list[WorkerHandle] = []
        self.model_version = 0

    def start(self) -> None:
        if self.workers:
            return
        self.workers = start_workers(self.cfg)
        self.push_weights_to_workers()

    def close(self) -> None:
        if self.workers:
            stop_workers(self.workers)
            self.workers = []

    def push_weights_to_workers(self) -> None:
        self.model_version += 1
        payload = {
            "op": "sync_weights",
            "state_dict": self._cpu_state_dict(self.learner_model),
            "model_version": self.model_version,
        }
        for w in self.workers:
            w.command_q.put(payload)

        for w in self.workers:
            msg = self._wait_worker_message(w, timeout_s=self.cfg.parallel.sync_timeout_s)
            if msg.get("op") != "synced":
                raise RuntimeError(f"Worker sync failed: {msg}")
            if int(msg.get("model_version", -1)) != self.model_version:
                raise RuntimeError(f"Worker synced wrong model version: {msg}")

    def collect_parallel(self, total_episodes: int, seed_base: int = 0) -> list[Sample]:
        if total_episodes <= 0:
            return []
        if not self.workers:
            raise RuntimeError("Workers are not started")

        base = total_episodes // len(self.workers)
        rem = total_episodes % len(self.workers)
        episodes_per_worker = [base + (1 if i < rem else 0) for i in range(len(self.workers))]

        for i, w in enumerate(self.workers):
            w.command_q.put({"op": "collect", "episodes": episodes_per_worker[i], "seed_base": seed_base})

        all_samples: list[Sample] = []
        for w in self.workers:
            msg = self._wait_worker_message(w, timeout_s=self.cfg.parallel.collect_timeout_s)
            if msg.get("op") != "collected":
                raise RuntimeError(f"Worker collect failed: {msg}")
            if int(msg.get("model_version", -1)) != self.model_version:
                raise RuntimeError(
                    f"Stale worker output: expected model_version={self.model_version}, got {msg.get('model_version')}"
                )
            all_samples.extend(msg.get("samples", []))

        return all_samples

    def train_iterations(self, num_iterations: int, seed_base: int = 0) -> list[IterationStats]:
        self.start()
        stats: list[IterationStats] = []

        for it in range(num_iterations):
            samples = self.collect_parallel(self.cfg.train.episodes_per_iteration, seed_base=seed_base + it * 10_000)
            self.replay.add_many(samples)

            lp, lv = self._optimize_steps(self.cfg.train.gradient_steps_per_iteration)

            # Barriered version sync after training; next collection uses this version.
            self.push_weights_to_workers()

            stats.append(
                IterationStats(
                    iteration=it,
                    collected_samples=len(samples),
                    replay_size=len(self.replay),
                    loss_policy=lp,
                    loss_value=lv,
                    model_version=self.model_version,
                )
            )
        return stats

    def _wait_worker_message(self, worker: WorkerHandle, timeout_s: float) -> dict[str, Any]:
        if timeout_s <= 0:
            timeout_s = 1.0
        try:
            msg = worker.result_q.get(timeout=timeout_s)
            return msg
        except queue.Empty as exc:
            if not worker.process.is_alive():
                raise RuntimeError(
                    f"Worker process {worker.process.pid} died while waiting for result."
                ) from exc
            raise RuntimeError(
                f"Timed out waiting {timeout_s}s for worker process {worker.process.pid} result."
            ) from exc

    def _optimize_steps(self, steps: int) -> tuple[float, float]:
        if steps <= 0:
            return 0.0, 0.0

        last_policy = 0.0
        last_value = 0.0
        self.learner_model.train()

        for _ in range(steps):
            if len(self.replay) < self.cfg.train.batch_size:
                break
            obs, pi, z = self.replay.sample_batch(self.cfg.train.batch_size)
            obs = obs.to(self.device, non_blocking=True)
            pi = pi.to(self.device, non_blocking=True)
            z = z.to(self.device, non_blocking=True)

            raw = self.learner_model(obs)
            probs, values = self._training_outputs(raw)

            log_probs = torch.log(probs + 1e-8)
            policy_loss = -(pi * log_probs).sum(dim=1).mean()
            value_loss = torch.nn.functional.mse_loss(values.reshape(-1), z)
            loss = policy_loss + self.cfg.train.value_coef * value_loss

            self.optimizer.zero_grad(set_to_none=True)
            loss.backward()
            self.optimizer.step()

            last_policy = float(policy_loss.detach().cpu().item())
            last_value = float(value_loss.detach().cpu().item())

        return last_policy, last_value

    @staticmethod
    def _training_outputs(raw: Any) -> tuple[torch.Tensor, torch.Tensor]:
        if isinstance(raw, tuple) and len(raw) == 2:
            probs, values = raw
            return torch.as_tensor(probs), torch.as_tensor(values).reshape(-1)
        raise TypeError(
            "Training expects model forward to return tuple(probs, values). "
            "Use a wrapper model for training if your model returns richer objects."
        )

    @staticmethod
    def _resolve_learner_device(learner_gpu_id: int) -> torch.device:
        if torch.cuda.is_available() and learner_gpu_id < torch.cuda.device_count():
            return torch.device(f"cuda:{learner_gpu_id}")
        return torch.device("cpu")

    @staticmethod
    def _cpu_state_dict(model: torch.nn.Module) -> dict[str, torch.Tensor]:
        return {k: v.detach().cpu() for k, v in model.state_dict().items()}
