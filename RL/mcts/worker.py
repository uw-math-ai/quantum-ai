from __future__ import annotations

import copy
from dataclasses import dataclass
import multiprocessing as mp
import queue
from typing import Any

import gymnasium as gym
import numpy as np
import torch
from gymnasium import spaces

from .config import AlphaZeroConfig
from .mcts import MCTSPlanner
from .model_adapter import infer_policy_value
from .replay_buffer import Sample


class DeepCopyGymAdapter:
    """Generic simulator adapter using deepcopy snapshots.

    This is simple and broadly compatible, but can be slow for large env objects.
    """

    def __init__(self, env: gym.Env[Any, int]) -> None:
        self.env = env
        self._obs: Any = None
        self._info: dict[str, Any] = {}

    @property
    def action_dim(self) -> int:
        if not isinstance(self.env.action_space, spaces.Discrete):
            raise TypeError("Only Discrete action spaces are supported in this MVP")
        return int(self.env.action_space.n)

    def reset(self, seed: int | None = None) -> tuple[Any, dict[str, Any]]:
        obs, info = self.env.reset(seed=seed)
        self._obs, self._info = obs, info
        return obs, info

    def clone_state(self) -> Any:
        get_state = getattr(self.env, "get_mcts_state", None)
        if callable(get_state):
            return (get_state(), copy.deepcopy(self._obs), copy.deepcopy(self._info))
        return copy.deepcopy((self.env, self._obs, self._info))

    def restore_state(self, state: Any) -> None:
        set_state = getattr(self.env, "set_mcts_state", None)
        if callable(set_state) and isinstance(state, tuple) and len(state) == 3:
            env_state, obs, info = state
            set_state(env_state)
            self._obs, self._info = copy.deepcopy(obs), copy.deepcopy(info)
            return
        self.env, self._obs, self._info = copy.deepcopy(state)

    def step(self, action: int) -> tuple[Any, float, bool, bool, dict[str, Any]]:
        obs, reward, terminated, truncated, info = self.env.step(action)
        self._obs, self._info = obs, info
        return obs, float(reward), bool(terminated), bool(truncated), info

    def legal_actions(self, obs: Any, info: dict[str, Any]) -> np.ndarray:
        return np.ones(self.action_dim, dtype=bool)


@dataclass
class WorkerHandle:
    process: Any
    command_q: mp.Queue
    result_q: mp.Queue


def _episode_to_samples(obs_list: list[Any], pi_list: list[np.ndarray], rewards: list[float], gamma: float) -> list[Sample]:
    z = 0.0
    returns = [0.0 for _ in rewards]
    for i in range(len(rewards) - 1, -1, -1):
        z = rewards[i] + gamma * z
        returns[i] = z
    return [Sample(obs=o, pi=p, z=r) for o, p, r in zip(obs_list, pi_list, returns)]


def _worker_main(
    worker_id: int,
    cfg: AlphaZeroConfig,
    assigned_gpu_id: int | None,
    command_q: mp.Queue,
    result_q: mp.Queue,
) -> None:
    env = cfg.env_factory()
    adapter = DeepCopyGymAdapter(env)

    model = cfg.model_factory()
    if assigned_gpu_id is not None and torch.cuda.is_available():
        device = torch.device(f"cuda:{assigned_gpu_id}")
    else:
        device = torch.device("cpu")
    model.to(device)
    model.eval()

    planner = MCTSPlanner(cfg.mcts)
    model_version = 0

    while True:
        try:
            cmd = command_q.get(timeout=1.0)
        except queue.Empty:
            continue

        op = cmd.get("op")
        if op == "close":
            break

        if op == "sync_weights":
            state_dict = cmd["state_dict"]
            with torch.no_grad():
                model.load_state_dict(state_dict, strict=True)
            model_version = int(cmd.get("model_version", model_version + 1))
            result_q.put({"op": "synced", "worker_id": worker_id, "model_version": model_version})
            continue

        if op == "collect":
            episodes = int(cmd["episodes"])
            seed_base = int(cmd.get("seed_base", 0))
            out_samples: list[Sample] = []

            for ep in range(episodes):
                obs, info = adapter.reset(seed=seed_base + ep + worker_id * 100_000)
                done = False
                obs_seq: list[Any] = []
                pi_seq: list[np.ndarray] = []
                rew_seq: list[float] = []

                while not done:
                    policy = planner.search(
                        env=adapter,
                        root_obs=obs,
                        root_info=info,
                        evaluate_fn=lambda x: infer_policy_value(
                            model=model,
                            obs=x,
                            action_dim=adapter.action_dim,
                            device=device,
                        ),
                    )
                    action = int(np.random.choice(adapter.action_dim, p=policy))
                    next_obs, reward, terminated, truncated, next_info = adapter.step(action)

                    obs_seq.append(obs)
                    pi_seq.append(policy)
                    rew_seq.append(float(reward))

                    obs, info = next_obs, next_info
                    done = bool(terminated or truncated)

                out_samples.extend(_episode_to_samples(obs_seq, pi_seq, rew_seq, cfg.mcts.gamma))

            result_q.put(
                {
                    "op": "collected",
                    "worker_id": worker_id,
                    "model_version": model_version,
                    "samples": out_samples,
                }
            )
            continue

        result_q.put({"op": "error", "worker_id": worker_id, "message": f"Unknown op: {op}"})


def start_workers(cfg: AlphaZeroConfig) -> list[WorkerHandle]:
    ctx = mp.get_context("spawn")
    gpu_ids = cfg.parallel.resolved_inference_gpu_ids()

    handles: list[WorkerHandle] = []
    for worker_id in range(cfg.parallel.num_cpu_workers):
        command_q: mp.Queue = ctx.Queue(maxsize=cfg.parallel.worker_queue_size)
        result_q: mp.Queue = ctx.Queue(maxsize=cfg.parallel.worker_queue_size)
        assigned_gpu_id = gpu_ids[worker_id % len(gpu_ids)] if gpu_ids else None

        p = ctx.Process(
            target=_worker_main,
            args=(worker_id, cfg, assigned_gpu_id, command_q, result_q),
            daemon=True,
        )
        p.start()
        handles.append(WorkerHandle(process=p, command_q=command_q, result_q=result_q))

    return handles


def stop_workers(handles: list[WorkerHandle]) -> None:
    for h in handles:
        h.command_q.put({"op": "close"})
    for h in handles:
        h.process.join(timeout=5)
        if h.process.is_alive():
            h.process.terminate()
            h.process.join(timeout=5)
