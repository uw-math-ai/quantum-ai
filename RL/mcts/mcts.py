from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

import numpy as np

from .config import MCTSConfig
from .model_adapter import PolicyValueOutput


class MCTSEnvAdapter(Protocol):
    @property
    def action_dim(self) -> int: ...

    def clone_state(self) -> Any: ...

    def restore_state(self, state: Any) -> None: ...

    def step(self, action: int) -> tuple[Any, float, bool, bool, dict[str, Any]]: ...

    def legal_actions(self, obs: Any, info: dict[str, Any]) -> np.ndarray: ...


EvaluateFn = Callable[[Any], PolicyValueOutput]


@dataclass
class TreeNode:
    state: Any
    obs: Any
    info: dict[str, Any]
    done: bool
    action_dim: int
    legal_mask: np.ndarray
    expanded: bool = False
    children: dict[int, "TreeNode"] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.legal_mask = self.legal_mask.astype(bool)
        self.N = np.zeros(self.action_dim, dtype=np.int32)
        self.W = np.zeros(self.action_dim, dtype=np.float32)
        self.Q = np.zeros(self.action_dim, dtype=np.float32)
        self.P = np.zeros(self.action_dim, dtype=np.float32)

    def expand(self, priors: np.ndarray) -> None:
        if priors.shape[0] != self.action_dim:
            raise ValueError("Prior size mismatch")
        masked = np.where(self.legal_mask, priors, 0.0)
        s = float(masked.sum())
        if s <= 0:
            legal_count = int(self.legal_mask.sum())
            if legal_count == 0:
                raise ValueError("No legal actions for expansion")
            masked = self.legal_mask.astype(np.float32) / legal_count
        else:
            masked = masked / s
        self.P = masked.astype(np.float32)
        self.expanded = True


class MCTSPlanner:
    def __init__(self, config: MCTSConfig) -> None:
        self.config = config

    def search(
        self,
        env: MCTSEnvAdapter,
        root_obs: Any,
        root_info: dict[str, Any],
        evaluate_fn: EvaluateFn,
    ) -> np.ndarray:
        root_state = env.clone_state()
        root = TreeNode(
            state=root_state,
            obs=root_obs,
            info=root_info,
            done=False,
            action_dim=env.action_dim,
            legal_mask=env.legal_actions(root_obs, root_info),
        )

        root_eval = evaluate_fn(root_obs)
        root.expand(root_eval.priors.numpy())

        for _ in range(self.config.num_simulations):
            env.restore_state(root.state)
            node = root
            path: list[tuple[TreeNode, int, float]] = []

            while node.expanded and not node.done:
                action = self._select_action(node)
                next_obs, reward, terminated, truncated, next_info = env.step(action)
                done = bool(terminated or truncated)
                path.append((node, action, float(reward)))

                child = node.children.get(action)
                if child is None:
                    child = TreeNode(
                        state=env.clone_state(),
                        obs=next_obs,
                        info=next_info,
                        done=done,
                        action_dim=env.action_dim,
                        legal_mask=env.legal_actions(next_obs, next_info),
                    )
                    node.children[action] = child
                    node = child
                    break
                node = child

            if node.done:
                leaf_value = 0.0
            else:
                leaf_eval = evaluate_fn(node.obs)
                node.expand(leaf_eval.priors.numpy())
                leaf_value = float(leaf_eval.value)

            v = leaf_value
            for parent, action, reward in reversed(path):
                v = reward + self.config.gamma * v
                parent.N[action] += 1
                parent.W[action] += v
                parent.Q[action] = parent.W[action] / max(parent.N[action], 1)

        env.restore_state(root.state)
        return self._visit_policy(root.N, root.legal_mask)

    def _select_action(self, node: TreeNode) -> int:
        c = self.config.c_puct
        total = float(np.sum(node.N))
        sqrt_total = np.sqrt(total + 1.0)

        bonus = c * node.P * sqrt_total / (1.0 + node.N)
        score = node.Q + bonus
        score = np.where(node.legal_mask, score, -np.inf)
        return int(np.argmax(score))

    def _visit_policy(self, visits: np.ndarray, legal_mask: np.ndarray) -> np.ndarray:
        tau = self.config.temperature
        counts = visits.astype(np.float64)
        counts = np.where(legal_mask, counts, 0.0)

        if tau <= 1e-8:
            pi = np.zeros_like(counts)
            if counts.sum() <= 0:
                legal = np.flatnonzero(legal_mask)
                pi[legal[0]] = 1.0
            else:
                pi[int(np.argmax(counts))] = 1.0
            return pi.astype(np.float32)

        scaled = np.power(counts, 1.0 / tau)
        s = scaled.sum()
        if s <= 0:
            legal = legal_mask.astype(np.float32)
            return (legal / legal.sum()).astype(np.float32)
        return (scaled / s).astype(np.float32)
