import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent.parent / "envs"))
sys.path.insert(0, str(Path(__file__).parent.parent / "data"))

from circuit_generation_env import CircuitGenerationEnv
from prompt_loader import PromptLoader
from local_model_agent import LocalModelAgent

import time
from typing import List, Dict
import json
import torch


class TrainingLogger:
    """Simple logger for training metrics."""
    
    def __init__(self, log_file: str = "training_log.jsonl"):
        self.log_file = log_file
        self.metrics_history = []
    
    def log(self, episode: int, metrics: Dict):
        entry = {"episode": episode, "timestamp": time.time(), **metrics}
        self.metrics_history.append(entry)
        
        # Append to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Print to console
        print(f"Episode {episode:4d} | "
              f"Train: {metrics.get('train_mean_reward', 0):6.2f} "
              f"(max: {metrics.get('train_max_reward', 0):6.2f}) | "
              f"Valid: {metrics.get('syntax_valid_pct', 0):5.1f}%", end="")
        
        if 'val_mean_reward' in metrics:
            print(f" | Val: {metrics['val_mean_reward']:6.2f}", end="")
        
        print()
    
    def save_best_circuits(self, circuits: List[str], rewards: List[float], 
                          stabilizers: List[List[str]], filename: str = "best_circuits.jsonl"):
        """Save best performing circuits."""
        best_data = []
        for circuit, reward, stabs in zip(circuits, rewards, stabilizers):
            best_data.append({
                "circuit": circuit,
                "reward": reward,
                "stabilizers": stabs
            })
        
        # Sort by reward descending
        best_data.sort(key=lambda x: x['reward'], reverse=True)
        
        with open(filename, 'w') as f:
            for entry in best_data:
                f.write(json.dumps(entry) + '\n')
        
        print(f"Saved {len(best_data)} circuits to {filename}")


class TrajectoryCollector:
    """Collect and save trajectories for RL training."""
    
    def __init__(self, traj_file: str = "trajectories.jsonl"):
        self.traj_file = traj_file
        self.trajectories = []
    
    def add_trajectory(
        self,
        stabilizers: List[str],
        circuit: str,
        reward: float,
        log_prob: float,
    ):
        """Add a single trajectory."""
        traj = {
            "stabilizers": stabilizers,
            "circuit": circuit,
            "reward": reward,
            "log_prob": log_prob,
        }
        self.trajectories.append(traj)
        
        # Write to file immediately
        with open(self.traj_file, 'a') as f:
            f.write(json.dumps(traj) + '\n')
    
    def get_statistics(self) -> Dict:
        """Get statistics about collected trajectories."""
        if not self.trajectories:
            return {}
        
        rewards = [t['reward'] for t in self.trajectories]
        log_probs = [t['log_prob'] for t in self.trajectories]
        
        return {
            'num_trajectories': len(self.trajectories),
            'mean_reward': sum(rewards) / len(rewards),
            'max_reward': max(rewards),
            'min_reward': min(rewards),
            'mean_log_prob': sum(log_probs) / len(log_probs),
        }


def train(
    num_episodes: int = 100,
    batch_size: int = 8,
    val_interval: int = 10,
    log_dir: str = "logs",
    model_name: str = "meta-llama/Llama-2-7b-hf",
    learning_rate: float = 1e-5,
    max_tokens: int = 256,
    temperature: float = 0.2,
    grad_clip: float = 1.0,
):
    """
    Main RL training loop for Agent A (REINFORCE).
    
    Args:
        num_episodes: Number of training episodes
        batch_size: Number of circuits per batch
        val_interval: Evaluate validation set every N episodes
        log_dir: Directory to save logs and trajectories
        model_name: Model to use for generation
        learning_rate: AdamW learning rate
        max_tokens: Max new tokens per generation
        temperature: Sampling temperature
        grad_clip: Gradient clipping norm
    """
    
    # Create log directory
    os.makedirs(log_dir, exist_ok=True)
    
    # Initialize agent and environment
    print("Initializing agent and environment...")
    agent = LocalModelAgent(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
    optimizer = torch.optim.AdamW(agent.model.parameters(), lr=learning_rate)
    env = CircuitGenerationEnv(
        data_path="reinforcement_learning/data/circuit_permute.jsonl"
    )
    
    # Load validation set
    val_loader = PromptLoader("reinforcement_learning/data/circuit_val.jsonl")
    val_prompts = []
    for _ in range(min(10, val_loader.total_count)):  # 10 validation examples
        val_prompts.append(val_loader.get_random_prompt())
    print(f"Loaded {len(val_prompts)} validation prompts")
    
    # Initialize loggers
    logger = TrainingLogger(log_file=os.path.join(log_dir, "training_log.jsonl"))
    traj_collector = TrajectoryCollector(traj_file=os.path.join(log_dir, "trajectories.jsonl"))
    
    # Track best rewards
    best_train_reward = float('-inf')
    best_circuits = []
    best_rewards = []
    best_stabilizers = []
    
    print(f"\n{'='*60}")
    print(f"Starting RL training: {num_episodes} episodes, batch_size={batch_size}")
    print(f"{'='*60}\n")
    
    # Training loop
    for episode in range(1, num_episodes + 1):
        # Get batch of training prompts
        batch = env.get_batch(batch_size)
        stabilizers_batch = [p['input_stabilizers'] for p in batch]
        
        # Generate circuits
        try:
            agent.model.eval()
            circuits, prompts = agent.generate_batch(stabilizers_batch)
        except Exception as e:
            print(f"Error generating batch: {e}")
            continue
        
        # Evaluate batch
        rewards, details = env.evaluate_batch(circuits, stabilizers_batch)
        
        # Compute log-probs with grad and update policy
        agent.model.train()
        log_probs = agent.compute_logprobs(prompts, circuits)
        rewards_t = torch.tensor(rewards, device=log_probs.device, dtype=torch.float32)
        advantages = rewards_t - rewards_t.mean()
        advantages = advantages / (advantages.std() + 1e-8)
        loss = -(advantages * log_probs).mean()

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(agent.model.parameters(), grad_clip)
        optimizer.step()

        # Collect trajectories
        log_probs_list = log_probs.detach().cpu().tolist()
        for stabs, circuit, reward, log_prob in zip(stabilizers_batch, circuits, rewards, log_probs_list):
            traj_collector.add_trajectory(stabs, circuit, float(reward), float(log_prob))
        
        # Compute metrics
        mean_reward = sum(rewards) / len(rewards)
        max_reward = max(rewards)
        syntax_valid_count = sum(1 for d in details if d['syntax_valid'])
        syntax_valid_pct = 100 * syntax_valid_count / len(details)
        
        metrics = {
            'train_mean_reward': mean_reward,
            'train_max_reward': max_reward,
            'syntax_valid_pct': syntax_valid_pct,
            'mean_log_prob': float(sum(log_probs_list) / len(log_probs_list)) if log_probs_list else 0.0,
            'loss': float(loss.item()),
        }
        
        # Track best circuits
        if mean_reward > best_train_reward:
            best_train_reward = mean_reward
            best_circuits = circuits.copy()
            best_rewards = rewards.copy()
            best_stabilizers = stabilizers_batch.copy()
        
        # Validation evaluation
        if episode % val_interval == 0:
            val_stabilizers = [p['input_stabilizers'] for p in val_prompts]
            try:
                agent.model.eval()
                val_circuits, _ = agent.generate_batch(val_stabilizers)
                val_rewards, _ = env.evaluate_batch(val_circuits, val_stabilizers)
                val_mean_reward = sum(val_rewards) / len(val_rewards)
                metrics['val_mean_reward'] = val_mean_reward
                metrics['val_max_reward'] = max(val_rewards)
            except Exception as e:
                print(f"Validation error: {e}")
        
        # Log metrics
        logger.log(episode, metrics)
    
    # Save best circuits
    print(f"\n{'='*60}")
    print(f"Collection complete!")
    print(f"Best training mean reward: {best_train_reward:.2f}")
    
    best_file = os.path.join(log_dir, "best_circuits.jsonl")
    logger.save_best_circuits(best_circuits, best_rewards, best_stabilizers, best_file)
    
    # Print trajectory statistics
    traj_stats = traj_collector.get_statistics()
    print(f"\nTrajectory Statistics:")
    for key, val in traj_stats.items():
        if isinstance(val, float):
            print(f"  {key}: {val:.4f}")
        else:
            print(f"  {key}: {val}")
    
    print(f"Trajectories saved to: {os.path.join(log_dir, 'trajectories.jsonl')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Agent A circuit generator')
    parser.add_argument('--episodes', type=int, default=100,
                        help='Number of training episodes (default: 100)')
    parser.add_argument('--batch-size', type=int, default=8,
                        help='Batch size (default: 8)')
    parser.add_argument('--val-interval', type=int, default=10,
                        help='Validation interval in episodes (default: 10)')
    parser.add_argument('--log-dir', type=str, default='reinforcement_learning/logs',
                        help='Directory for logs (default: reinforcement_learning/logs)')
    parser.add_argument('--model', type=str, default='meta-llama/Llama-2-7b-hf',
                        help='Model name from HuggingFace Hub')
    parser.add_argument('--lr', type=float, default=1e-5,
                        help='Learning rate (default: 1e-5)')
    parser.add_argument('--max-tokens', type=int, default=256,
                        help='Max new tokens per generation (default: 256)')
    parser.add_argument('--temperature', type=float, default=0.2,
                        help='Sampling temperature (default: 0.2)')
    parser.add_argument('--grad-clip', type=float, default=1.0,
                        help='Gradient clipping norm (default: 1.0)')
    
    args = parser.parse_args()
    
    train(
        num_episodes=args.episodes,
        batch_size=args.batch_size,
        val_interval=args.val_interval,
        log_dir=args.log_dir,
        model_name=args.model,
        learning_rate=args.lr,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        grad_clip=args.grad_clip,
    )
