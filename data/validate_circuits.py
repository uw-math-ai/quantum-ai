#!/usr/bin/env python3
"""
Validate all circuits in generated_circuits.json by checking if they are 
stabilized by their generators using the check_stabilizers function.

Outputs results to a JSON file with:
- code_name: The name of the code
- circuit: The circuit string
- stabilized: List of stabilizers that were preserved
- not_stabilized: List of stabilizers that were not preserved  
- stabilizer_fraction: Fraction of stabilizers that were preserved
"""

import argparse
import json
import sys
import os

# Add parent directory to path to import from tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.check_stabilizers import check_stabilizers


def validate_circuits(input_file: str, output_file: str) -> None:
    """Validate all circuits in the input file and write results to output file.
    
    Args:
        input_file: Path to the generated_circuits.json file
        output_file: Path to write the validation results
    """
    # Load the circuits
    with open(input_file, 'r') as f:
        circuits = json.load(f)
    
    results = []
    
    for i, entry in enumerate(circuits):
        code_name = entry.get('code_name', f'Unknown_{i}')
        circuit = entry.get('circuit', '')
        generators = entry.get('generators', [])
        
        print(f"Validating {code_name}...")
        
        try:
            # Check which stabilizers are preserved
            stabilizer_results = check_stabilizers(circuit, generators)
            
            # Separate into stabilized and not stabilized
            stabilized = [s for s, is_stable in stabilizer_results.items() if is_stable]
            not_stabilized = [s for s, is_stable in stabilizer_results.items() if not is_stable]
            
            # Calculate fraction
            total = len(generators)
            fraction = len(stabilized) / total if total > 0 else 0.0
            
            result = {
                'code_name': code_name,
                'circuit': circuit,
                'stabilized': stabilized,
                'not_stabilized': not_stabilized,
                'stabilizer_fraction': fraction
            }
            
            status = "✓" if fraction == 1.0 else "✗"
            print(f"  {status} {len(stabilized)}/{total} stabilizers preserved ({fraction:.2%})")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            result = {
                'code_name': code_name,
                'circuit': circuit,
                'stabilized': [],
                'not_stabilized': generators,
                'stabilizer_fraction': 0.0,
                'error': str(e)
            }
        
        results.append(result)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Write results to output file
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    total_circuits = len(results)
    fully_stabilized = sum(1 for r in results if r['stabilizer_fraction'] == 1.0)
    partially_stabilized = sum(1 for r in results if 0 < r['stabilizer_fraction'] < 1.0)
    not_stabilized_count = sum(1 for r in results if r['stabilizer_fraction'] == 0.0)
    
    print(f"\n{'='*50}")
    print(f"Validation Summary")
    print(f"{'='*50}")
    print(f"Total circuits validated: {total_circuits}")
    print(f"Fully stabilized (100%): {fully_stabilized}")
    print(f"Partially stabilized: {partially_stabilized}")
    print(f"Not stabilized (0%): {not_stabilized_count}")
    print(f"\nResults written to: {output_file}")


# To run this script, use the following command line format:
# python validate_circuits.py --input data/generated_circuits.json --output data/validation_results.json
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Validate circuits by checking if they are stabilized by their generators.'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Path to the input JSON file containing circuits to validate'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Path to write the validation results JSON file'
    )
    
    args = parser.parse_args()
    validate_circuits(args.input, args.output)
