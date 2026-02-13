import json
import os
import sys
import argparse

# Add tools directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import generate_state_prep


def generate_circuits_from_benchmarks(
    benchmarks_path: str,
    output_path: str,
    attempts: int = 3,
    timeout: int = 60
) -> list[dict]:
    """
    Generate fault-tolerant state preparation circuits for all stabilizer groups in benchmarks.
    
    Args:
        benchmarks_path: Path to the benchmarks JSON file
        output_path: Path to save the output JSON file
        attempts: Number of attempts for each circuit generation
        timeout: Timeout in seconds for each generation
    
    Returns:
        List of dictionaries with code_name, generators, and circuit
    """
    with open(benchmarks_path, 'r') as f:
        benchmarks = json.load(f)
    
    results = []
    
    count = 0
    for i, benchmark in enumerate(benchmarks):
        code_name = benchmark.get("name")
        generators = benchmark.get("generators")
        logical_qubits = benchmark.get("logical_qubits", 1)
        if logical_qubits!= 4:
            continue
        if (count == 3):
            break
        count += 1
        
        if not code_name or not generators:
            print(f"[{i+1}/{len(benchmarks)}] Skipping entry with missing name or generators")
            continue
        
        print(f"[{i+1}/{len(benchmarks)}] Generating circuit for: {code_name}")
        # print(f"  Generators: {generators}")
        
        try:
            circuit = generate_state_prep(
                stabilizers=generators,
                attempts=attempts,
                timeout=timeout,
                logical_qubits=logical_qubits
            )
            
            if circuit is not None:
                circuit_str = str(circuit)
                print(f"  ✓ Circuit generated successfully")
            else:
                circuit_str = None
                print(f"  ✗ Failed to generate circuit")
                
        except Exception as e:
            circuit_str = None
            print(f"  ✗ Error: {e}")
        
        result = {
            "code_name": code_name,
            "generators": generators,
            "circuit": circuit_str
        }
        results.append(result)
        
        # Save intermediate results after each generation
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"  Saved intermediate results to {output_path}")
    
    print(f"\nGeneration complete. {len(results)} circuits saved to {output_path}")
    return results

# To run this script, use the following command line format:
# python generate_state_prep_circuits.py --benchmarks data/benchmarks.json --output data/generated_circuits.json --attempts 3 --timeout 60
def main():
    parser = argparse.ArgumentParser(
        description="Generate fault-tolerant circuits for all stabilizer groups in benchmarks"
    )
    parser.add_argument(
        "--benchmarks", 
        default="data/benchmarks.json",
        help="Path to benchmarks JSON file"
    )
    parser.add_argument(
        "--output", 
        default="data/generated_circuits.json",
        help="Path to output JSON file"
    )
    parser.add_argument(
        "--attempts", 
        type=int, 
        default=1,
        help="Number of attempts for each circuit generation"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=300,
        help="Timeout in seconds for each generation"
    )
    
    args = parser.parse_args()
    
    generate_circuits_from_benchmarks(
        benchmarks_path=args.benchmarks,
        output_path=args.output,
        attempts=args.attempts,
        timeout=args.timeout
    )


if __name__ == "__main__":
    main()
