#!/usr/bin/env python3
"""
Verify all circuit examples in circuit_dataset.jsonl
Outputs True/False for each example indicating if the circuit correctly prepares the target stabilizers.
"""

import json
import sys
import os

# Add tools directory to path to import check_stabilizers
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools'))
from check_stabilizers import check_stabilizers


def verify_circuit_entry(entry: dict) -> bool:
    """
    Verify a single circuit entry from the dataset.
    
    Args:
        entry: Dictionary with 'input_stabilizers' and 'output_circuit' keys
        
    Returns:
        True if the circuit correctly prepares all target stabilizers, False otherwise
    """
    try:
        # Extract data
        stabilizers = entry['input_stabilizers']
        circuit_str = entry['output_circuit'].replace('\\n', '\n')
        
        # Check if circuit preserves all stabilizers
        results = check_stabilizers(circuit_str, stabilizers)
        
        # All stabilizers must be preserved
        return all(results.values())
        
    except Exception as e:
        # If there's an error, the circuit is considered incorrect
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify circuits in dataset')
    parser.add_argument('input', nargs='?', default='dataset_generation/circuit_dataset.jsonl',
                        help='Input JSONL file (default: dataset_generation/circuit_dataset.jsonl)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output for failed examples')
    parser.add_argument('--summary', '-s', action='store_true',
                        help='Show summary statistics only')
    parser.add_argument('--limit', '-l', type=int, default=None,
                        help='Limit number of examples to check')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found")
        return 1
    
    # Read and verify each entry
    passed = 0
    failed = 0
    failed_entries = []
    
    with open(args.input, 'r') as f:
        for i, line in enumerate(f, 1):
            if args.limit and i > args.limit:
                break
                
            entry = json.loads(line)
            is_valid = verify_circuit_entry(entry)
            
            if is_valid:
                passed += 1
            else:
                failed += 1
                failed_entries.append((i, entry))
            
            # Print result for each example (unless summary only)
            if not args.summary:
                print(f"Example {i}: {is_valid}")
    
    # Print summary
    print("\n" + "="*60)
    print(f"SUMMARY:")
    print(f"Total checked: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {100 * passed / (passed + failed):.2f}%")
    
    # Show details of failed examples if requested
    if args.verbose and failed_entries:
        print("\n" + "="*60)
        print("FAILED EXAMPLES:")
        for idx, entry in failed_entries:
            print(f"\nExample {idx}:")
            print(f"  Code: {entry['source_code']}")
            print(f"  Permutation: {entry['permutation']}")
            print(f"  Stabilizers: {entry['input_stabilizers']}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
