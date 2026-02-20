"""
Step-based policy for CircuitBuilderEnv.
"""

from __future__ import annotations

from typing import List, Tuple, Union

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical


class StepBasedCircuitAgent(nn.Module):
    """MLP policy/value network with shared backbone for step-based circuit building."""

    def __init__(
        self,
        observation_shape: Tuple[int, ...],
        action_space_n: Union[int, np.ndarray, list, tuple],
        hidden_size: int = 1024,
        device: str | None = None,
    ) -> None:
        super().__init__()
        self.observation_shape = observation_shape
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        input_dim = int(np.prod(observation_shape))

        # Shared backbone
        self.backbone = nn.Sequential(
            nn.Linear(input_dim, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
        )

        # Support MultiDiscrete action spaces
        if isinstance(action_space_n, (np.ndarray, tuple, list)):
            self.action_dims = [int(n) for n in action_space_n]
        else:
            self.action_dims = [int(action_space_n)]

        # Lightweight policy heads (one linear layer each)
        self.policy_heads = nn.ModuleList([
            nn.Linear(hidden_size, n) for n in self.action_dims
        ])

        # Value head
        self.value_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1),
        )
        self.to(self.device)

    def _prep_obs(self, obs: np.ndarray) -> torch.Tensor:
        obs_tensor = torch.as_tensor(obs, dtype=torch.float32, device=self.device)
        if obs_tensor.shape == torch.Size(self.observation_shape):
            obs_tensor = obs_tensor.unsqueeze(0)
        return obs_tensor.view(obs_tensor.shape[0], -1)

    def forward(self, obs: np.ndarray):
        x = self._prep_obs(obs)
        features = self.backbone(x)
        logits_list = [head(features) for head in self.policy_heads]
        value = self.value_head(features).squeeze(-1)
        return logits_list, value

    def act(
        self,
        obs: np.ndarray,
        return_entropy: bool = False,
    ):
        logits_list, value = self.forward(obs)
        actions = []
        log_probs = []
        entropies = []
        for logits in logits_list:
            dist = Categorical(logits=logits)
            a = dist.sample()
            actions.append(a.item())
            log_probs.append(dist.log_prob(a))
            entropies.append(dist.entropy())
        action = actions if len(actions) > 1 else actions[0]
        log_prob = torch.stack(log_probs).sum()
        entropy = torch.stack(entropies).mean()
        if return_entropy:
            return action, log_prob, value, entropy
        return action, log_prob, value

    def evaluate(
        self,
        obs_batch: np.ndarray,
        actions_batch: np.ndarray,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Re-evaluate a batch of (obs, action) pairs under the current policy.

        Args:
            obs_batch: array of shape (batch, *obs_shape)
            actions_batch: array of shape (batch,) for Discrete or (batch, num_dims) for MultiDiscrete

        Returns:
            log_probs: (batch,) summed log-prob across action dims
            values: (batch,)
            entropy: (batch,) mean entropy across action dims
        """
        logits_list, values = self.forward(obs_batch)

        actions_tensor = torch.as_tensor(actions_batch, dtype=torch.long, device=self.device)
        if actions_tensor.dim() == 1 and len(self.action_dims) > 1:
            actions_tensor = actions_tensor.unsqueeze(-1)

        all_log_probs = []
        all_entropies = []
        for i, logits in enumerate(logits_list):
            dist = Categorical(logits=logits)
            if len(self.action_dims) > 1:
                a = actions_tensor[:, i]
            else:
                a = actions_tensor
            all_log_probs.append(dist.log_prob(a))
            all_entropies.append(dist.entropy())

        log_probs = torch.stack(all_log_probs, dim=-1).sum(dim=-1)
        entropy = torch.stack(all_entropies, dim=-1).mean(dim=-1)
        return log_probs, values, entropy

    def action_probs(self, obs: np.ndarray) -> list:
        logits_list, _ = self.forward(obs)
        probs_list = [torch.softmax(logits, dim=-1) for logits in logits_list]
        return [probs.detach().cpu().numpy().squeeze(0) for probs in probs_list]