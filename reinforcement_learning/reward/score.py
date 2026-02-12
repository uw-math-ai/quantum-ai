"""
Reward scoring engine for two-agent quantum circuit RL system.

Agent A (Generator): Generates circuits from stabilizers
Agent B (FT Enforcer): Makes circuits fault-tolerant

Each agent has its own reward model optimized for its task.
"""

import stim
import sys
import os
from typing import List, Dict, Tuple

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Verification (Alt)'))

from check_stabilizers import check_stabilizers
from fault_tolerance_checker import FaultToleranceChecker


class GeneratorRewardModel:
    """
    Reward model for Agent A: Circuit Generator.
    
    Goal: Generate valid circuits that satisfy target stabilizers with minimal gates.
    """
    
    def __init__(self, 
                 syntax_weight: float = 1.0,
                 stabilizer_weight: float = 10.0,
                 depth_penalty: float = 0.02,
                 gate_penalty: float = 0.01,
                 compactness_bonus: float = 5.0):
        """
        Initialize Generator reward model.
        
        Args:
            syntax_weight: Reward for valid Stim syntax
            stabilizer_weight: Reward per satisfied stabilizer
            depth_penalty: Penalty per unit of circuit depth
            gate_penalty: Penalty per gate
            compactness_bonus: Bonus for achieving all stabilizers with few gates
        """
        self.syntax_weight = syntax_weight
        self.stabilizer_weight = stabilizer_weight
        # self.depth_penalty = depth_penalty
        # self.gate_penalty = gate_penalty
        # self.compactness_bonus = compactness_bonus
    
    def score_circuit(self, 
                     circuit_str: str, 
                     target_stabilizers: List[str]) -> Tuple[float, Dict]:
        """
        Score a generated circuit.
        
        Args:
            circuit_str: Stim circuit string
            target_stabilizers: List of target stabilizer strings
            
        Returns:
            (total_reward, details_dict)
        """
        details = {
            'syntax_valid': False,
            'stabilizers_satisfied': 0,
            'stabilizers_total': len(target_stabilizers),
            'circuit_depth': 0,
            'gate_count': 0,
            'syntax_reward': 0.0,
            'stabilizer_reward': 0.0,
            # 'compactness_reward': 0.0,
            # 'depth_penalty_value': 0.0,
            # 'gate_penalty_value': 0.0,
            'total_reward': 0.0
        }
        
        # 1. Check syntax validity
        try:
            circuit = stim.Circuit(circuit_str)
            details['syntax_valid'] = True
            details['syntax_reward'] = self.syntax_weight
            details['gate_count'] = len(circuit)
            details['circuit_depth'] = self._compute_depth(circuit)
        except Exception as e:
            details['total_reward'] = -10.0
            details['error'] = str(e)
            return details['total_reward'], details
        
        # 2. Check stabilizer satisfaction
        try:
            stab_results = check_stabilizers(circuit_str, target_stabilizers)
            num_satisfied = sum(stab_results.values())
            details['stabilizers_satisfied'] = num_satisfied
            details['stabilizer_reward'] = num_satisfied * self.stabilizer_weight
            
            # # Compactness bonus if all stabilizers satisfied
            # if num_satisfied == len(target_stabilizers):
            #     threshold = len(target_stabilizers) * 10
            #     gate_efficiency = max(0,threshold  - details['gate_count']) / 50.0
            #     details['compactness_reward'] = self.compactness_bonus * gate_efficiency
        except Exception as e:
            details['stabilizer_error'] = str(e)
            details['stabilizer_reward'] = 0.0
        
        # # 3. Apply penalties
        # details['depth_penalty_value'] = -self.depth_penalty * details['circuit_depth']
        # details['gate_penalty_value'] = -self.gate_penalty * details['gate_count']
        
        # 4. Compute total reward
        details['total_reward'] = (
            details['syntax_reward'] +
            details['stabilizer_reward']
            #+ details['compactness_reward'] +
            # details['depth_penalty_value'] +
            # details['gate_penalty_value']
        )
        
        return details['total_reward'], details
    
    def _compute_depth(self, circuit: stim.Circuit) -> int:
        """Compute circuit depth (critical path length)."""
        if circuit.num_qubits == 0:
            return 0
        
        qubit_depth = [0] * circuit.num_qubits
        
        for instruction in circuit:
            if hasattr(instruction, 'targets_copy'):
                targets = [t.value for t in instruction.targets_copy() if hasattr(t, 'value')]
                if targets:
                    max_depth = max(qubit_depth[q] for q in targets if q < len(qubit_depth))
                    for q in targets:
                        if q < len(qubit_depth):
                            qubit_depth[q] = max_depth + 1
        
        return max(qubit_depth) if qubit_depth else 0


class FTEnforcerRewardModel:
    """
    Reward model for Agent B: Fault-Tolerance Enforcer.
    
    Goal: Transform valid circuits into fault-tolerant versions while preserving stabilizers.
    """
    
    def __init__(self, 
                 ft_success_reward: float = 50.0,
                 stabilizer_preservation_weight: float = 20.0,
                 gate_overhead_penalty: float = 0.02,
                 stabilizer_violation_penalty: float = 30.0):
        """
        Initialize FT Enforcer reward model.
        
        Args:
            ft_success_reward: Reward for achieving fault tolerance
            stabilizer_preservation_weight: Reward per preserved stabilizer
            gate_overhead_penalty: Penalty per added gate
            stabilizer_violation_penalty: Penalty per broken stabilizer
        """
        self.ft_success_reward = ft_success_reward
        self.stabilizer_preservation_weight = stabilizer_preservation_weight
        self.gate_overhead_penalty = gate_overhead_penalty
        self.stabilizer_violation_penalty = stabilizer_violation_penalty
    
    def score_circuit(self, 
                     original_circuit_str: str,
                     modified_circuit_str: str, 
                     target_stabilizers: List[str],
                     num_data_qubits: int = None) -> Tuple[float, Dict]:
        """
        Score an FT-enforced circuit.
        
        Args:
            original_circuit_str: Original circuit from Generator
            modified_circuit_str: FT-enforced version from Agent B
            target_stabilizers: Target stabilizers (must be preserved)
            num_data_qubits: Number of data qubits for FT checking
            
        Returns:
            (total_reward, details_dict)
        """
        details = {
            'modified_syntax_valid': False,
            'stabilizers_preserved': 0,
            'stabilizers_total': len(target_stabilizers),
            'fault_tolerant': False,
            'original_gate_count': 0,
            'modified_gate_count': 0,
            'gate_overhead': 0,
            'ft_violations': 0,
            'ft_reward': 0.0,
            'stabilizer_reward': 0.0,
            'overhead_penalty_value': 0.0,
            'violation_penalty_value': 0.0,
            'total_reward': 0.0
        }
        
        # Get original gate count
        try:
            original_circuit = stim.Circuit(original_circuit_str)
            details['original_gate_count'] = len(original_circuit)
        except:
            details['original_gate_count'] = 0
        
        # 1. Check modified circuit syntax
        try:
            modified_circuit = stim.Circuit(modified_circuit_str)
            details['modified_syntax_valid'] = True
            details['modified_gate_count'] = len(modified_circuit)
            details['gate_overhead'] = details['modified_gate_count'] - details['original_gate_count']
        except Exception as e:
            details['total_reward'] = -50.0
            details['error'] = str(e)
            return details['total_reward'], details
        
        # 2. Check stabilizer preservation
        try:
            stab_results = check_stabilizers(modified_circuit_str, target_stabilizers)
            num_preserved = sum(stab_results.values())
            num_violated = len(target_stabilizers) - num_preserved
            
            details['stabilizers_preserved'] = num_preserved
            details['stabilizer_reward'] = num_preserved * self.stabilizer_preservation_weight
            details['violation_penalty_value'] = -num_violated * self.stabilizer_violation_penalty
        except Exception as e:
            details['stabilizer_error'] = str(e)
            details['violation_penalty_value'] = -len(target_stabilizers) * self.stabilizer_violation_penalty
        
        # 3. Check fault tolerance (only if stabilizers preserved)
        if details['stabilizers_preserved'] == len(target_stabilizers):
            try:
                ft_checker = FaultToleranceChecker(
                    modified_circuit,
                    num_data_qubits=num_data_qubits
                )
                is_ft, violations = ft_checker.check_fault_tolerance()
                details['fault_tolerant'] = is_ft
                details['ft_violations'] = len(violations)
                
                if is_ft:
                    details['ft_reward'] = self.ft_success_reward
                else:
                    # Partial credit based on how close to FT
                    partial_credit = max(0, 1.0 - len(violations) / 10.0)
                    details['ft_reward'] = self.ft_success_reward * partial_credit * 0.5
            except Exception as e:
                details['ft_error'] = str(e)
                details['ft_reward'] = 0.0
        
        # 4. Apply gate overhead penalty
        if details['gate_overhead'] > 0:
            details['overhead_penalty_value'] = -self.gate_overhead_penalty * details['gate_overhead']
        
        # 5. Compute total reward
        details['total_reward'] = (
            details['ft_reward'] +
            details['stabilizer_reward'] +
            details['overhead_penalty_value'] +
            details['violation_penalty_value']
        )
        
        return details['total_reward'], details


def score_generator(circuit_str: str, target_stabilizers: List[str]) -> float:
    """Convenience function for Agent A scoring."""
    model = GeneratorRewardModel()
    reward, _ = model.score_circuit(circuit_str, target_stabilizers)
    return reward


def score_ft_enforcer(original_circuit_str: str,
                      modified_circuit_str: str,
                      target_stabilizers: List[str],
                      num_data_qubits: int = None) -> float:
    """Convenience function for Agent B scoring."""
    model = FTEnforcerRewardModel()
    reward, _ = model.score_circuit(original_circuit_str, modified_circuit_str, 
                                    target_stabilizers, num_data_qubits)
    return reward


if __name__ == "__main__":
    print("="*60)
    print("AGENT A (Generator) Test")
    print("="*60)
    
    gen_model = GeneratorRewardModel()
    
    test_circuit = """
H 0
CX 0 1
CX 1 2
CX 2 3
"""
    
    test_stabilizers = ["XXXX", "ZIZI", "IZZI", "IIZZ"]
    
    reward, details = gen_model.score_circuit(test_circuit, test_stabilizers)
    
    print("\nREWARD BREAKDOWN:")
    for key, value in details.items():
        print(f"  {key:25s}: {value}")
    print(f"\nTOTAL REWARD: {reward:.3f}")
    
    print("\n" + "="*60)
    print("AGENT B (FT Enforcer) Test")
    print("="*60)
    
    # ft_model = FTEnforcerRewardModel()
    
    # # Simulate FT-modified circuit (just add some gates for demo)
    # modified_circuit = test_circuit + "H 0\n"
    
    # reward, details = ft_model.score_circuit(test_circuit, modified_circuit, 
    #                                          test_stabilizers, num_data_qubits=4)
    
    # print("\nREWARD BREAKDOWN:")
    # for key, value in details.items():
    #     print(f"  {key:25s}: {value}")
    # print(f"\nTOTAL REWARD: {reward:.3f}")
