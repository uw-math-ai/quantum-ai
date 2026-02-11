import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))

from score import GeneratorRewardModel, FTEnforcerRewardModel
from prompt_loader import PromptLoader

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test specific circuits from dataset')
    parser.add_argument('--jsonl', type=str, default='reinforcement_learning/data/circuit_permute.jsonl',
                        help='Path to circuit_dataset.jsonl')
    parser.add_argument('--index', type=int, default=0,
                        help='Index of circuit to test (default: 0)')
    parser.add_argument('--agent', type=str, default='a',
                        help='Agent to test: a (Generator) or b (FT Enforcer)')
    
    args = parser.parse_args()
    
    # Load circuit using PromptLoader
    loader = PromptLoader(args.jsonl)
    
    if args.index >= len(loader):
        print(f"Circuit at index {args.index} not found (max index: {len(loader)-1})")
        exit(1)
    
    circuit_data = loader[args.index]
    
    print(f"Testing circuit #{args.index}")
    print(f"Source: {circuit_data['source_code']}")
    print(f"Stabilizers: {circuit_data['input_stabilizers']}")
    print(f"Circuit: {circuit_data['output_circuit'][:100]}...")
    
    if args.agent.lower() == 'a':
        model = GeneratorRewardModel()
        reward, details = model.score_circuit(
            circuit_data['output_circuit'].replace('\\n', '\n'),
            circuit_data['input_stabilizers']
        )
        print(f"\nAgent A Reward: {reward:.3f}")
        for key, value in details.items():
            print(f"  {key}: {value}")
    else:
        print("Agent B test requires original + modified circuit")