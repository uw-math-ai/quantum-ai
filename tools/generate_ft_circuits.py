import json
import os
import sys
import argparse
import stim

# # Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import prompt_agent, validate_circuit, CircuitParam, generate_ft_state_prep
from copilot.tools import define_tool

def generate_circuits_from_data(
    benchmarks_path: str,
    output_path: str,
    attempts: int = 3,
    timeout: int = 60
) -> list[dict]:
    """
    Generate fault-tolerant state preparation circuits for all circuits in circuit_dataset.
    
    Args:
        benchmarks_path: Path to the circuits_dataset JSON file
        output_path: Path to save the output JSON file
        attempts: Number of attempts for each circuit generation
        timeout: Timeout in seconds for each generation
    
    Returns:
        List of dictionaries with code_name and circuit
    """
    results = []
    with open("data/circuit_dataset.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            source_code = entry["source_code"]
            distance = entry["d"]
            qubits = entry["permutation"]
            input_stabilizers = entry["input_stabilizers"]
            output_circuit = entry["output_circuit"]

            try:
                circuit = generate_ft_state_prep(
                    stabilizers=input_stabilizers,
                    non_ft_circuit = output_circuit,
                    distance = distance,
                    qubits = qubits,
                    attempts=attempts,
                    timeout=timeout
                )
                
                if circuit is not None:
                    if isinstance(circuit, list):
                        circuit_str = "\n".join(circuit)
                    else:
                        circuit_str = str(circuit)
                    print(f"  ✓ Circuit generated successfully")
                else:
                    circuit_str = None
                    print(f"  ✗ Failed to generate circuit")
                    
            except Exception as e:
                circuit_str = None
                print(f"  ✗ Error: {e}")
            
            result = {
                "code_name": entry["source_code"],
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
        description="Generate fault-tolerant circuits for all circuits"
    )
    parser.add_argument(
        "--benchmarks", 
        default="data/circuit_dataset.jsonl",
        help="Path to benchmarks JSONL file"
    )
    parser.add_argument(
        "--output", 
        default="data/generated_ft_circuits.json",
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
    
    generate_circuits_from_data(
        benchmarks_path=args.benchmarks,
        output_path=args.output,
        attempts=args.attempts,
        timeout=args.timeout
    )


if __name__ == "__main__":
    main()
