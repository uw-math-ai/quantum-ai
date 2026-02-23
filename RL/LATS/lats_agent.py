"""
LATS (Language Agent Tree Search) for Quantum Circuit Generation.

Uses llama-index's official LATS implementation with tools that wrap
the CircuitBuilderEnv gym environment.

Source paper: https://arxiv.org/pdf/2310.04406v2.pdf
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
from RL.envs.CircuitBuilderEnv import CircuitBuilderEnv, CircuitBuilderConfig
import mqt.qecc.codes as qecc


class CircuitBuilderLATSAgent:
    """
    LATS agent wrapper for CircuitBuilderEnv using llama-index's official implementation.
    
    Creates tools that interface with the gym environment and uses LATS
    for tree search-based exploration.
    """
    
    def __init__(
        self,
        env: CircuitBuilderEnv,
        llm: CopilotWrapper,
        num_expansions: int = 3,
        max_rollouts: int = 10,
        verbose: bool = True
    ):
        """
        Initialize LATS agent for circuit building.
        
        Args:
            env: CircuitBuilderEnv instance
            llm: CopilotWrapper LLM instance
            num_expansions: Number of candidate actions to generate per state
            max_rollouts: Maximum rollouts for tree search
            verbose: Print debug information
        """
        self.env = env
        self.llm = llm
        self.verbose = verbose
        
        # Track current environment state
        self.current_obs = None
        self.current_reward = 0.0
        self.is_done = False
        self.step_count = 0
        self.history = []
        
        # Create tools for the agent
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
        """Create tools for the LATS agent to interact with the environment."""
        
        tools = []
        
        # Tool: Apply one-qubit gate
        def apply_one_qubit_gate(gate: str, target: int) -> str:
            """
            Apply a one-qubit gate to the circuit.
            
            Args:
                gate: Gate name (H, X, Y, Z, S)
                target: Target qubit index
            
            Returns:
                Result message with reward and circuit state
            """
            if self.is_done:
                return "Circuit is already terminated. Cannot add more gates."
            
            try:
                action = self.env.action_to_int((gate, target))
                obs, reward, done, truncated, info = self.env.step(action)
                
                self.current_obs = obs
                self.current_reward += reward
                self.is_done = done or truncated
                self.step_count += 1
                self.history.append({"gate": gate, "target": target, "reward": reward})
                
                result = f"Applied {gate} to qubit {target}. "
                result += f"Reward: {reward:.3f}, Total: {self.current_reward:.3f}. "
                
                if "invalid_action" in info:
                    result += f"Warning: {info['invalid_action']} "
                
                if self.is_done:
                    result += "Circuit terminated. "
                    if "stabilizers_preservation" in info:
                        preserved = sum(1 for v in info["stabilizers_preservation"].values() if v)
                        total = len(info["stabilizers_preservation"])
                        result += f"Stabilizers preserved: {preserved}/{total}. "
                
                return result
                
            except Exception as e:
                return f"Error: {str(e)}"
        
        # Tool: Apply two-qubit gate
        def apply_two_qubit_gate(gate: str, control: int, target: int) -> str:
            """
            Apply a two-qubit gate to the circuit.
            
            Args:
                gate: Gate name (CNOT)
                control: Control qubit index
                target: Target qubit index
            
            Returns:
                Result message with reward and circuit state
            """
            if self.is_done:
                return "Circuit is already terminated. Cannot add more gates."
            
            try:
                action = self.env.action_to_int((gate, control, target))
                obs, reward, done, truncated, info = self.env.step(action)
                
                self.current_obs = obs
                self.current_reward += reward
                self.is_done = done or truncated
                self.step_count += 1
                self.history.append({
                    "gate": gate,
                    "control": control,
                    "target": target,
                    "reward": reward
                })
                
                result = f"Applied {gate} with control={control}, target={target}. "
                result += f"Reward: {reward:.3f}, Total: {self.current_reward:.3f}. "
                
                if "invalid_action" in info:
                    result += f"Warning: {info['invalid_action']} "
                
                if self.is_done:
                    result += "Circuit terminated. "
                    if "stabilizers_preservation" in info:
                        preserved = sum(1 for v in info["stabilizers_preservation"].values() if v)
                        total = len(info["stabilizers_preservation"])
                        result += f"Stabilizers preserved: {preserved}/{total}. "
                
                return result
                
            except Exception as e:
                return f"Error: {str(e)}"
        
        # Tool: Terminate circuit (measure flag qubits)
        def measure() -> str:
            """
            Terminate the circuit by measuring flag qubits.
            
            Returns:
                Final result with stabilizer preservation info
            """
            if self.is_done:
                return "Circuit is already terminated."
            
            try:
                action = self.env.action_to_int("M")
                obs, reward, done, truncated, info = self.env.step(action)
                
                self.current_obs = obs
                self.current_reward += reward
                self.is_done = True
                self.history.append({"action": "measure", "reward": reward})
                
                result = f"Circuit terminated. Final reward: {self.current_reward:.3f}. "
                
                if "stabilizers_preservation" in info:
                    stab_results = info["stabilizers_preservation"]
                    preserved = sum(1 for v in stab_results.values() if v)
                    total = len(stab_results)
                    result += f"Stabilizers preserved: {preserved}/{total}. "
                    
                    if preserved == total:
                        result += "SUCCESS: All stabilizers preserved!"
                    else:
                        failed = [k for k, v in stab_results.items() if not v]
                        result += f"FAILED: Missing stabilizers: {failed}"
                
                return result
                
            except Exception as e:
                return f"Error: {str(e)}"
        
        # Tool: Get circuit status
        def get_circuit_status() -> str:
            """
            Get current status of the circuit being built.
            
            Returns:
                Circuit statistics and current state
            """
            circuit_str = self.env.render() if self.env.render_mode else "No render available"
            
            status = f"Circuit depth: {self.step_count}/{self.env.config.max_gates}. "
            status += f"Total reward: {self.current_reward:.3f}. "
            status += f"Terminated: {self.is_done}. "
            status += f"\nCurrent circuit:\n{circuit_str}"
            
            return status
        
        # Create FunctionTools
        tools.append(FunctionTool.from_defaults(
            fn=apply_one_qubit_gate,
            name="apply_one_qubit_gate",
            description=(
                "Apply a one-qubit gate to the quantum circuit. "
                f"Available gates: {', '.join(self.env.config.one_qubit_gates)}. "
                f"Total qubits: {self.env.total_qubits} "
                f"(data: 0-{self.env.config.num_data_qubits-1}, "
                f"flag: {self.env.config.num_data_qubits}-{self.env.total_qubits-1})"
            )
        ))
        
        tools.append(FunctionTool.from_defaults(
            fn=apply_two_qubit_gate,
            name="apply_two_qubit_gate",
            description=(
                "Apply a two-qubit gate to the quantum circuit. "
                f"Available gates: {', '.join(self.env.config.two_qubit_gates)}. "
                f"Total qubits: {self.env.total_qubits}"
            )
        ))
        
        tools.append(FunctionTool.from_defaults(
            fn=measure,
            name="measure",
            description=(
                "Measure the flag qubits as the final action to terminate the circuit."
            )
        ))
        
        tools.append(FunctionTool.from_defaults(
            fn=get_circuit_status,
            name="get_circuit_status",
            description="Get the current status and structure of the circuit being built."
        ))
        
        return tools
    
    def reset(self) -> np.ndarray:
        """Reset the environment to initial state."""
        self.current_obs = self.env.reset()
        self.current_reward = 0.0
        self.is_done = False
        self.step_count = 0
        self.history = []
        return self.current_obs
    
    def run(self, task_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Run LATS agent to build a circuit.
        
        Args:
            task_description: Optional custom task description. If None, uses default.
        
        Returns:
            Dictionary with results including circuit, reward, and history
        """
        # Reset environment
        self.reset()
        
        # Build task description
        if task_description is None:
            stabilizers = self.env.stab_code.stabs_as_pauli_strings()
            stabilizers_str = ", ".join(stabilizers)
            
            task_description = (
                f"Build a quantum circuit for stabilizer state: {stabilizers_str}. "
                f"Available gates:\n" 
                f"- single-qubit gates ({', '.join(self.env.config.one_qubit_gates)}). Apply these by calling apply_one_qubit_gate with gate name and target qubit index.\n"
                f"- two-qubit gates ({', '.join(self.env.config.two_qubit_gates)}). Apply these by calling apply_two_qubit_gate with gate name and control/target qubit indices.\n"
                f"- Standard basis measurements. Apply this by calling the measure tool. A measurement is the last action to terminate the circuit.\n"
                f"Data qubit indexes: 0..{self.env.config.num_data_qubits-1}\n"
                f"Flag qubit indexes: {self.env.config.num_data_qubits}..{self.env.total_qubits-1}\n"
                f"PRIMARY GOAL: build a circuit that preserves all stabilizers.\n"
                f"SECONDARY GOAL: maximize ft_score.\n"
                f"TERTIARY GOAL: minimize the number of gates in the circuit.\n"
            )
        
        if self.verbose:
            print(f"\nTask: {task_description}\n")
            print("="*60)
        
        # Run agent
        try:
            response = self.agent.chat(task_description)
            
            if self.verbose:
                print("="*60)
                print(f"\nAgent response:\n{response}")
        
        except Exception as e:
            if self.verbose:
                print(f"\nAgent execution error: {e}")
        
        # Get final circuit
        final_circuit = self.env.render() if self.env.render_mode else str(self.env.circ)
        
        # Return results
        return {
            "circuit": final_circuit,
            "total_reward": self.current_reward,
            "step_count": self.step_count,
            "is_done": self.is_done,
            "history": self.history,
            "success": self.is_done and self.current_reward > 0
        }


def run_lats_example():
    """Example usage of LATS agent with llama-index."""
    
    # Create environment
    stabilizers = [
        "XXX",
        "ZZI",
        "IZZ"
    ]
    
    code = qecc.StabilizerCode(generators=stabilizers, distance=1, n=3)
    
    env_config = CircuitBuilderConfig(
        max_gates=32,
        num_data_qubits=3,
        num_flag_qubits=3
    )
    
    env = CircuitBuilderEnv(code, config=env_config, render_mode="string")
    
    # Create LLM
    llm = CopilotWrapper(
        model="ollama:ministral-3:8b",
        temperature=0.5,
        timeout=300  # Increased timeout for longer searches
    )
    
    # Create LATS agent
    agent = CircuitBuilderLATSAgent(
        env=env,
        llm=llm,
        num_expansions=3,
        max_rollouts=10,
        verbose=True
    )
    
    # Run agent
    print("Starting LATS agent...")
    results = agent.run()
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Success: {results['success']}")
    print(f"Total reward: {results['total_reward']:.3f}")
    print(f"Steps taken: {results['step_count']}")
    print(f"\nFinal circuit:")
    print(results['circuit'])
    print("\nAction history:")
    for i, action in enumerate(results['history']):
        print(f"  {i+1}. {action}")


if __name__ == "__main__":
    run_lats_example()
