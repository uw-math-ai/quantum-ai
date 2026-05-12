from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True)
class PolicyValueOutput:
    priors: torch.Tensor  # shape: (A,)
    value: float


def _to_tensor_obs(obs: Any, device: torch.device) -> torch.Tensor:
    if isinstance(obs, torch.Tensor):
        x = obs
    else:
        x = torch.as_tensor(obs)
    if x.ndim == 1:
        x = x.unsqueeze(0)
    return x.to(device=device, dtype=torch.float32)


def _normalize_priors(priors_like: torch.Tensor, action_dim: int) -> torch.Tensor:
    priors = priors_like.reshape(-1)
    if priors.numel() != action_dim:
        raise ValueError(
            f"Policy size mismatch: expected {action_dim}, got {priors.numel()}"
        )
    priors = torch.clamp(priors, min=0.0)
    s = priors.sum()
    if s <= 0:
        priors = torch.full_like(priors, 1.0 / action_dim)
    else:
        priors = priors / s
    return priors


def normalize_model_output(raw_output: Any, action_dim: int) -> PolicyValueOutput:
    """Normalize common model outputs to (priors, value).

    Supported patterns:
    - tuple(probs, value)
    - object with attributes policy_probs and values (StatePrep-style)
    """
    if isinstance(raw_output, tuple) and len(raw_output) == 2:
        policy_like, value_like = raw_output
        policy_like = torch.as_tensor(policy_like)
        # Treat tuple policy output as probabilities.
        priors = _normalize_priors(policy_like, action_dim)
        value = float(torch.as_tensor(value_like).reshape(-1)[0].item())
        return PolicyValueOutput(priors=priors, value=value)

    if hasattr(raw_output, "policy_probs") and hasattr(raw_output, "values"):
        policy_probs = getattr(raw_output, "policy_probs")
        values = getattr(raw_output, "values")
        if isinstance(policy_probs, list):
            if len(policy_probs) == 0:
                raise ValueError("policy_probs list is empty")
            if len(policy_probs) != 1:
                raise ValueError(
                    "Expected unbatched policy_probs list of length 1 during MCTS inference. "
                    f"Got length {len(policy_probs)}."
                )
            priors_like = torch.as_tensor(policy_probs[0])
        else:
            priors_like = torch.as_tensor(policy_probs)
        priors = _normalize_priors(priors_like, action_dim)
        value = float(torch.as_tensor(values).reshape(-1)[0].item())
        return PolicyValueOutput(priors=priors, value=value)

    raise TypeError(f"Unsupported model output type: {type(raw_output)!r}")


@torch.no_grad()
def infer_policy_value(model: torch.nn.Module, obs: Any, action_dim: int, device: torch.device) -> PolicyValueOutput:
    x = _to_tensor_obs(obs, device=device)
    raw = model(x)
    out = normalize_model_output(raw, action_dim)
    return PolicyValueOutput(priors=out.priors.detach().cpu(), value=out.value)
