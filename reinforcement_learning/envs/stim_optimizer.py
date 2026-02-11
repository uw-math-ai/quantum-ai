"""
Batch reward computation for RL training.
"""

import sys
import os
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'reward'))

from check_stabilizers import check_stabilizers
from score import GeneratorRewardModel, FTEnforcerRewardModel
"""
Batch reward computation for RL training.
"""

import sys
import os
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'reward'))

from check_stabilizers import check_stabilizers
from score import GeneratorRewardModel, FTEnforcerRewardModel


class RewardComputer:
    
    def __init__(self):
        self.gen_reward_model = GeneratorRewardModel()
        self.ft_reward_model = FTEnforcerRewardModel()
    
    def fast_syntax_check(self, circuit_str: str) -> bool:
        try:
            from stim import Circuit
            Circuit(circuit_str)
            return True
        except:
            return False
    
    def batch_check_stabilizers(
        self, 
        circuit_strs: List[str], 
        stabilizer_sets: List[List[str]]
    ) -> List[Dict[str, bool]]:
        results = []
        
        for circuit_str, stabilizers in zip(circuit_strs, stabilizer_sets):
            try:
                stab_results = check_stabilizers(circuit_str, stabilizers)
                results.append(stab_results)
            except:
                results.append({s: False for s in stabilizers})
        
        return results
    
    def batch_compute_rewards_agent_a(
        self,
        circuit_strs: List[str],
        stabilizer_sets: List[List[str]]
    ) -> Tuple[List[float], List[Dict]]:
        rewards = []
        details_list = []
        
        for circuit_str, stabilizers in zip(circuit_strs, stabilizer_sets):
            reward, details = self.gen_reward_model.score_circuit(
                circuit_str,
                stabilizers
            )
            rewards.append(reward)
            details_list.append(details)
        
        return rewards, details_list
    
    def batch_compute_rewards_agent_b(
        self,
        original_circuits: List[str],
        modified_circuits: List[str],
        stabilizer_sets: List[List[str]],
        num_data_qubits: int = None
    ) -> Tuple[List[float], List[Dict]]:
        rewards = []
        details_list = []
        
        for orig, mod, stabs in zip(original_circuits, modified_circuits, stabilizer_sets):
            reward, details = self.ft_reward_model.score_circuit(
                orig,
                mod,
                stabs,
                num_data_qubits
            )
            rewards.append(reward)
            details_list.append(details)
        
        return rewards, details_list

