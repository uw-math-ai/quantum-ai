"""
Simple LATS test with CartPole environment.

Tests if LATS agent framework works correctly with a basic gym environment
before debugging CircuitBuilderEnv-specific issues.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import gymnasium as gym

# Add parent directories to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from llama_index.agent.lats import LATSAgentWorker
from llama_index.core.agent import AgentRunner
from llama_index.core.tools import FunctionTool, BaseTool

from CopilotWrapper import CopilotWrapper


class CartPoleLATSAgent:
    """
    LATS agent wrapper for CartPole using llama-index's official implementation.
    
    Simple test to verify LATS framework works before debugging CircuitBuilderEnv.
    """
    
    def __init__(
        self,
        llm: CopilotWrapper,
        num_expansions: int = 2,
        max_rollouts: int = 5,
        verbose: bool = True
    ):
        """
        Initialize LATS agent for CartPole.
        
        Args:
            llm: CopilotWrapper LLM instance
            num_expansions: Number of candidate actions per state
            max_rollouts: Maximum rollouts for tree search
            verbose: Print debug information
        """
        self.env = gym.make("CartPole-v1")
        self.llm = llm
        self.verbose = verbose
        
        # Track state
        self.current_obs = None
        self.current_reward = 0.0
        self.step_count = 0
        self.is_done = False
        self.history = []
        
        # Create tools
        tools = self._create_tools()
        
        # Create LATS worker
        self.worker = LATSAgentWorker(
            tools=tools,
            llm=llm,
            num_expansions=num_expansions,
            max_rollouts=max_rollouts,
            verbose=verbose
        )
        
        # Create agent runner
        self.agent = AgentRunner(self.worker)
    
    def _create_tools(self) -> List[BaseTool]:
        """Create tools for CartPole control."""
        
        tools = []
        
        def push_left() -> str:
            """Push the cart to the left (action 0)."""
            if self.is_done:
                return "Episode finished. Cannot apply more actions."
            
            try:
                obs, reward, done, truncated, info = self.env.step(0)
                self.current_obs = obs
                self.current_reward += reward
                self.is_done = done or truncated
                self.step_count += 1
                self.history.append({"action": "push_left", "reward": reward})
                
                x, x_dot, theta, theta_dot = obs
                result = (
                    f"Pushed left. Reward: {reward:.1f}, Total: {self.current_reward:.1f}. "
                    f"State: x={x:.2f}, θ={theta:.3f}, done={self.is_done}."
                )
                return result
            except Exception as e:
                return f"Error: {str(e)}"
        
        def push_right() -> str:
            """Push the cart to the right (action 1)."""
            if self.is_done:
                return "Episode finished. Cannot apply more actions."
            
            try:
                obs, reward, done, truncated, info = self.env.step(1)
                self.current_obs = obs
                self.current_reward += reward
                self.is_done = done or truncated
                self.step_count += 1
                self.history.append({"action": "push_right", "reward": reward})
                
                x, x_dot, theta, theta_dot = obs
                result = (
                    f"Pushed right. Reward: {reward:.1f}, Total: {self.current_reward:.1f}. "
                    f"State: x={x:.2f}, θ={theta:.3f}, done={self.is_done}."
                )
                return result
            except Exception as e:
                return f"Error: {str(e)}"
        
        def get_status() -> str:
            """Get current CartPole state."""
            if self.current_obs is None:
                return "Episode not started yet."
            
            x, x_dot, theta, theta_dot = self.current_obs
            status = (
                f"Step: {self.step_count}/200. Total reward: {self.current_reward:.1f}. "
                f"Position: x={x:.3f}, velocity={x_dot:.3f}, "
                f"Angle: θ={theta:.3f}rad, angular_vel={theta_dot:.3f}. "
                f"Done: {self.is_done}."
            )
            return status
        
        tools.append(FunctionTool.from_defaults(
            fn=push_left,
            name="push_left",
            description="Push the cart to the left (action 0). Use when pole tilts right."
        ))
        
        tools.append(FunctionTool.from_defaults(
            fn=push_right,
            name="push_right",
            description="Push the cart to the right (action 1). Use when pole tilts left."
        ))
        
        tools.append(FunctionTool.from_defaults(
            fn=get_status,
            name="get_status",
            description="Get current CartPole state (position, angle, velocity, reward)."
        ))
        
        return tools
    
    def reset(self) -> np.ndarray:
        """Reset the environment."""
        self.current_obs, _ = self.env.reset()
        self.current_reward = 0.0
        self.is_done = False
        self.step_count = 0
        self.history = []
        return self.current_obs
    
    def run(self, num_steps: int = 10) -> Dict[str, Any]:
        """
        Run LATS agent for CartPole.
        
        Args:
            num_steps: Approximate number of steps to take
        
        Returns:
            Results with reward, steps, and history
        """
        self.reset()
        
        task = (
            "Balance the CartPole. The pole starts upright. "
            "If it tilts left (θ < 0), push right. If it tilts right (θ > 0), push left. "
            "Try to keep the pole balanced (|θ| < 0.2) for as many steps as possible. "
            f"Goal: achieve {num_steps} successful steps. Check status frequently."
        )
        
        if self.verbose:
            print(f"\nTask: {task}\n")
            print("="*60)
        
        try:
            response = self.agent.chat(task)
            
            if self.verbose:
                print("="*60)
                print(f"\nAgent response:\n{response}")
        except Exception as e:
            if self.verbose:
                print(f"\nAgent error: {e}")
        
        return {
            "reward": self.current_reward,
            "steps": self.step_count,
            "done": self.is_done,
            "history": self.history,
            "success": self.current_reward >= 100
        }


def test_cartpole_lats():
    """Test LATS with CartPole environment."""
    
    print("="*60)
    print("LATS Agent Test: CartPole")
    print("="*60)
    
    # Create LLM
    llm = CopilotWrapper(
        model="gpt-4.1",
        temperature=0.5,
        timeout=300
    )
    
    # Create LATS agent
    agent = CartPoleLATSAgent(
        llm=llm,
        num_expansions=2,
        max_rollouts=5,
        verbose=True
    )
    
    # Run agent
    print("\nStarting CartPole LATS agent...")
    results = agent.run(num_steps=50)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Success: {results['success']}")
    print(f"Reward: {results['reward']:.1f}")
    print(f"Steps: {results['steps']}")
    print(f"Done: {results['done']}")
    print("\nAction history:")
    for i, action in enumerate(results['history'][-10:]):  # Last 10 actions
        print(f"  {i+1}. {action}")


if __name__ == "__main__":
    test_cartpole_lats()
