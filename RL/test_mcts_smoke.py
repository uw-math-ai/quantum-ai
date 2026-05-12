import sys
from pathlib import Path
import torch
import torch.nn as nn
import stim

# Ensure we can import from the RL directory
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from RL.envs.BackwardStatePrepEnv import BackwardStatePrepEnv
from RL.mcts.config import AlphaZeroConfig, MCTSConfig, TrainConfig, ParallelConfig
from RL.mcts.alphazero_agent import AlphaZeroAgent

class MockProbModel(nn.Module):
    """A minimal mock model that predicts probabilities and a value state."""
    def __init__(self, obs_shape: tuple, action_dim: int):
        super().__init__()
        # Flatten observation
        in_features = 1
        for dim in obs_shape:
            in_features *= dim
            
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features, 64), # Fix back to dynamic sizes but let's reshape correctly
            nn.ReLU()
        )
        self.policy_head = nn.Linear(64, action_dim)
        self.value_head = nn.Linear(64, 1)

    def forward(self, x):
        # Flatten correctly regardless of batch size
        x = x.view(x.shape[0], -1) if x.ndim > 2 else x.view(1, -1) if x.ndim == 2 else x
        features = self.fc(x)
        
        # Explicitly output PROBABILITIES (sum to 1) for the policy
        logits = self.policy_head(features)
        probs = torch.softmax(logits, dim=-1)
        
        # Value between -1 and 1
        value = torch.tanh(self.value_head(features))
        
        return probs, value

def env_factory():
    # 2-qubit Bell state stabilizers: XX, ZZ
    target_stabs = [stim.PauliString(s) for s in ["XX", "ZZ"]]
    circ = stim.Tableau.from_stabilizers(target_stabs, allow_underconstrained=True).to_circuit()
    return BackwardStatePrepEnv(circ)

def model_factory():
    # We need to know the dims. Let's create a temp env.
    temp_env = env_factory()
    obs_shape = temp_env.observation_space.shape
    action_dim = temp_env.action_space.n
    return MockProbModel(obs_shape, action_dim)

def test_pipeline():
    print("Initializing AlphaZero configuration...")
    
    cfg = AlphaZeroConfig(
        env_factory=env_factory,
        model_factory=model_factory,
        mcts=MCTSConfig(
            num_simulations=4,  # Tiny number of sims for fast testing
            c_puct=1.5
        ),
        train=TrainConfig(
            episodes_per_iteration=4,        # 4 total episodes
            gradient_steps_per_iteration=2,  # 2 gradient updates
            batch_size=8
        ),
        parallel=ParallelConfig(
            num_cpu_workers=2,               # Use 2 parallel workers
            worker_queue_size=4
        )
    )

    print("Starting AlphaZero Agent...")
    agent = AlphaZeroAgent(cfg)

    try:
        print("Running 2 iterations of training (collect -> train -> sync)...")
        stats = agent.train_iterations(num_iterations=2)
        
        for stat in stats:
            print(f"\nIteration {stat.iteration} Summary:")
            print(f"  - Collected Samples: {stat.collected_samples}")
            print(f"  - Replay Buffer Size: {stat.replay_size}")
            print(f"  - Policy Loss: {stat.loss_policy:.4f}")
            print(f"  - Value Loss: {stat.loss_value:.4f}")
            print(f"  - Model Version Deployed: {stat.model_version}")
            
        print("\n✅ End-to-end test completed successfully!")
        
    finally:
        print("Shutting down workers...")
        agent.close()

if __name__ == "__main__":
    test_pipeline()
