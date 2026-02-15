"""
Minimal step-based PPO training loop for CircuitBuilderEnv.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

import numpy as np
import torch
import gymnasium as gym

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "envs"))

from step_agent import StepBasedCircuitAgent
from circuit_builder_env_wrapper import CircuitBuilderEnvWrapper

# Reuse existing logger
sys.path.insert(0, str(Path(__file__).parent))
from train_agent_a import TrainingLogger

# Import CircuitBuilderConfig from RL/envs
ROOT_DIR = Path(__file__).resolve().parents[2]
RL_ENVS_DIR = ROOT_DIR / "RL" / "envs"
sys.path.insert(0, str(RL_ENVS_DIR))
from CircuitBuilderEnv import CircuitBuilderConfig


def compute_gae(
    rewards: torch.Tensor,
    values: torch.Tensor,
    dones: torch.Tensor,
    gamma: float = 0.99,
    lam: float = 0.95,
    next_value: float = 0.0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Compute GAE advantages and returns, respecting episode boundaries.

    Args:
        rewards: (T, num_envs)
        values: (T, num_envs)
        dones: (T, num_envs) — 1.0 if episode ended, 0.0 otherwise
        gamma: discount factor
        lam: GAE lambda
        next_value: bootstrap value for last step

    Returns:
        advantages: (T, num_envs)
        returns: (T, num_envs)
    """
    T, num_envs = rewards.shape
    advantages = torch.zeros_like(rewards)
    last_gae = torch.zeros(num_envs)

    for t in reversed(range(T)):
        if t == T - 1:
            next_val = torch.full((num_envs,), next_value)
        else:
            next_val = values[t + 1]
        mask = 1.0 - dones[t]
        delta = rewards[t] + gamma * next_val * mask - values[t]
        last_gae = delta + gamma * lam * mask * last_gae
        advantages[t] = last_gae

    returns = advantages + values
    return advantages, returns


def train(
    jsonl_path: str,
    num_episodes: int = 200,
    max_steps: int = 128,
    gamma: float = 0.99,
    lr: float = 3e-4,
    num_qubits: int = 20,
) -> None:
    # ---------- Hyperparameters ----------
    num_envs = 8
    rollout_length = 1024        # steps per env per rollout
    minibatch_size = 256
    update_epochs = 4
    clip_eps = 0.2
    vf_coef = 0.5
    ent_coef = 0.005
    max_grad_norm = 0.5
    gae_lambda = 0.95
    total_timesteps = num_episodes * max_steps

    # ---------- Environment setup ----------
    config = CircuitBuilderConfig(max_gates=max_steps, num_qubits=num_qubits)

    def make_env():
        return CircuitBuilderEnvWrapper(jsonl_path, config=config, render_mode=None)

    env_fns = [make_env for _ in range(num_envs)]
    vec_env = gym.vector.SyncVectorEnv(env_fns)

    # Use single_* to get per-env spaces (not batched)
    obs_shape = vec_env.single_observation_space.shape
    single_action_space = vec_env.single_action_space
    if hasattr(single_action_space, "nvec"):
        action_space_n = single_action_space.nvec
        multi_discrete = True
    else:
        action_space_n = single_action_space.n
        multi_discrete = False

    print(f"Observation shape: {obs_shape}")
    print(f"Action space: {single_action_space}")
    print(f"Action dims: {action_space_n}")
    print(f"Num qubits: {num_qubits}")
    print(f"Total timesteps: {total_timesteps}")

    # ---------- Agent & optimizer ----------
    agent = StepBasedCircuitAgent(
        observation_shape=obs_shape,
        action_space_n=action_space_n,
    )
    optimizer = torch.optim.Adam(agent.parameters(), lr=lr)

    # ---------- Logger ----------
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = TrainingLogger(log_file=str(logs_dir / "training_step_agent.jsonl"))

    # ---------- Training loop ----------
    total_steps = 0
    obs, _ = vec_env.reset()  # (num_envs, *obs_shape)

    while total_steps < total_timesteps:
        # ------- Rollout collection -------
        all_obs = []           # (T, num_envs, *obs_shape)
        all_actions = []       # (T, num_envs) or (T, num_envs, action_dims)
        all_log_probs = []     # (T, num_envs)
        all_values = []        # (T, num_envs)
        all_rewards = []       # (T, num_envs)
        all_dones = []         # (T, num_envs)
        all_entropies = []     # (T, num_envs)
        all_invalid = []       # (T, num_envs)

        for _step in range(rollout_length):
            step_actions = []
            step_log_probs = []
            step_values = []
            step_entropies = []

            for i in range(num_envs):
                a, lp, v, ent = agent.act(obs[i], return_entropy=True)
                step_actions.append(a)
                step_log_probs.append(lp)
                step_values.append(v)
                step_entropies.append(ent)

            # Format actions for vec_env.step
            if multi_discrete:
                actions_array = np.array(step_actions, dtype=np.int64)  # (num_envs, num_dims)
            else:
                actions_array = np.array(step_actions, dtype=np.int64)  # (num_envs,)

            next_obs, reward, done, truncated, info = vec_env.step(actions_array)

            # Store
            all_obs.append(obs.copy())
            all_actions.append(np.array(step_actions))
            all_log_probs.append(torch.stack(step_log_probs).detach().squeeze(-1))
            all_values.append(torch.stack(step_values).detach().squeeze(-1))
            all_rewards.append(torch.tensor(reward, dtype=torch.float32))
            all_dones.append(torch.tensor(done | truncated, dtype=torch.float32))
            all_entropies.append(torch.stack(step_entropies).detach().squeeze(-1))
            all_invalid.append(
                np.array([info[i].get("invalid_action", False) if isinstance(info, (list, tuple))
                          else info.get("invalid_action", np.zeros(num_envs, dtype=bool))[i]
                          for i in range(num_envs)])
            )

            obs = next_obs
            total_steps += num_envs

        # ------- Stack rollout data -------
        obs_tensor = torch.tensor(np.array(all_obs), dtype=torch.float32)
        actions_tensor = torch.tensor(np.array(all_actions), dtype=torch.long)
        old_log_probs = torch.stack(all_log_probs)
        values = torch.stack(all_values)
        rewards = torch.stack(all_rewards)
        dones = torch.stack(all_dones)
        entropies = torch.stack(all_entropies)
        invalid_flags = np.array(all_invalid)

        # ------- GAE -------
        advantages, returns = compute_gae(
            rewards, values, dones, gamma=gamma, lam=gae_lambda
        )
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # ------- Flatten for mini-batching -------
        batch_size = rollout_length * num_envs
        flat_obs = obs_tensor.reshape(batch_size, *obs_shape)
        if multi_discrete:
            flat_actions = actions_tensor.reshape(batch_size, -1)
        else:
            flat_actions = actions_tensor.reshape(batch_size)
        flat_old_log_probs = old_log_probs.reshape(batch_size)
        flat_advantages = advantages.reshape(batch_size)
        flat_returns = returns.reshape(batch_size)

        # ------- PPO updates -------
        for epoch in range(update_epochs):
            indices = torch.randperm(batch_size)
            for start in range(0, batch_size, minibatch_size):
                end = min(start + minibatch_size, batch_size)
                mb_idx = indices[start:end]

                mb_obs = flat_obs[mb_idx].numpy()
                mb_actions = flat_actions[mb_idx].numpy()
                mb_old_lp = flat_old_log_probs[mb_idx].to(agent.device)
                mb_adv = flat_advantages[mb_idx].to(agent.device)
                mb_ret = flat_returns[mb_idx].to(agent.device)

                # Recompute under current policy
                new_log_probs, new_values, new_entropy = agent.evaluate(mb_obs, mb_actions)

                # PPO clipped surrogate
                ratio = (new_log_probs - mb_old_lp).exp()
                surr1 = ratio * mb_adv
                surr2 = torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * mb_adv
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value loss
                value_loss = 0.5 * (mb_ret - new_values).pow(2).mean()

                # Entropy bonus
                entropy_loss = -new_entropy.mean()

                loss = policy_loss + vf_coef * value_loss + ent_coef * entropy_loss

                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(agent.parameters(), max_grad_norm)
                optimizer.step()

        # ------- Logging -------
        avg_reward = rewards.mean().item()
        avg_entropy = entropies.mean().item()
        invalid_rate = invalid_flags.mean()
        ep_returns = rewards.sum(dim=0).mean().item()

        logger.log(
            total_steps,
            {
                "batch_mean_reward": avg_reward,
                "episode_return": ep_returns,
                "batch_size": batch_size,
                "invalid_action_rate": float(invalid_rate),
                "policy_loss": float(policy_loss.item()),
                "value_loss": float(value_loss.item()),
                "loss": float(loss.item()),
                "entropy": float(avg_entropy),
            },
        )
        print(
            f"Step {total_steps:>8d} | "
            f"Reward={avg_reward:.4f} | "
            f"EpRet={ep_returns:.2f} | "
            f"Entropy={avg_entropy:.4f} | "
            f"V_Loss={value_loss.item():.4f}"
        )
        # ------- Periodic checkpoint -------
        save_dir = Path(__file__).parent.parent / "checkpoints"
        save_dir.mkdir(parents=True, exist_ok=True)
        torch.save(agent.state_dict(), save_dir / "step_agent_ppo.pt")

    vec_env.close()

    # Save model
    save_dir = Path(__file__).parent.parent / "checkpoints"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / "step_agent_ppo.pt"
    torch.save(agent.state_dict(), save_path)
    print(f"Model saved to {save_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jsonl",
        type=str,
        default=os.path.abspath(
            os.path.join(Path(__file__).parent.parent, "data", "circuit_small.jsonl")
        ),
        help="Path to dataset file",
    )
    parser.add_argument("--num_episodes", type=int, default=10000, help="Number of episodes")
    parser.add_argument("--max_steps", type=int, default=128, help="Max steps per episode")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--num_qubits", type=int, default=20, help="Number of qubits")
    args = parser.parse_args()

    train(
        args.jsonl,
        num_episodes=args.num_episodes,
        max_steps=args.max_steps,
        lr=args.lr,
        num_qubits=args.num_qubits,
    )