import json
import os
import sys
import argparse
import stim

# # Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from agent import prompt_agent, CircuitParam, generate_ft_state_prep
from copilot.tools import define_tool
from validate_ft_circuits import check_syndrome_extraction_ft
from check_error_propagation import check_fault_tolerance, ft_score
from check_stabilizers import check_stabilizers
from agent import generated_ft_circuits

generated_ft_circuits.clear()

def generate_circuits_from_data(
    benchmarks_path: str,
    output_path: str,
    model: str =  "claude-sonnet-4.5",
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
            generated_ft_circuits.clear()
            entry = json.loads(line)
            source_code = entry["source_code"]
            distance = entry["d"]
            qubits = entry["permutation"]
            input_stabilizers = entry["input_stabilizers"]
            output_circuit = entry["output_circuit"]
            ancillas = []
            start_time = None
            end_time = None

            # Compute FT score of the original (non-FT) circuit
            orig_ancillas = []
            clean_circuit = output_circuit.replace("\\n", "\n")
            orig_ft_score = ft_score(clean_circuit, qubits, orig_ancillas, distance, 1.0)
            print(f"Original FT score: {orig_ft_score}")
            try:
                start_time = datetime.now()

                circuit_results, all_candidates = generate_ft_state_prep(
                    stabilizers=input_stabilizers,
                    non_ft_circuit = output_circuit,
                    distance = distance,
                    qubits = qubits,
                    attempts=attempts,
                    timeout=timeout,
                    model=model
                )
                end_time = datetime.now()
                # generated_candidates = list(generated_ft_circuits)
                # generated_candidates = []
                # best_candidate = None
                # best_score = -1

                # for circ in generated_ft_circuits:
                #     try:
                #         circ_str = str(circ)

                #         used_qubits = set()
                #         for inst in circ:
                #             for t in inst.targets_copy():
                #                 if hasattr(t, "value"):
                #                     used_qubits.add(t.value)

                #         data_qubits = set(qubits)
                #         anc = sorted(list(used_qubits - data_qubits))

                #         score = ft_score(circ_str, qubits, anc, distance, 1.0)

                #         candidate = {
                #             "circuit": circ_str,
                #             "ft_score": score
                #         }

                #         generated_candidates.append(candidate)

                #         if score > best_score:
                #             best_score = score
                #             best_candidate = candidate

                #     except Exception as e:
                #         print(f"Skipping invalid generated circuit: {e}")
                

                if circuit_results is not None:
                    circuit_obj = circuit_results["circuit"]
                    circuit_str = str(circuit_obj)
                    temp = circuit_str.split()

                    used_qubits = set()
                    for inst in circuit_obj:
                        for t in inst.targets_copy():
                            if hasattr(t, "value"):
                                used_qubits.add(t.value)

                    data_qubits = set(qubits)
                    ancillas = sorted(list(used_qubits - data_qubits))

                    stab_results = check_stabilizers(circuit_str, input_stabilizers)
                    all_stabilized = all(stab_results.values())
                    print(f" ✓ stabilizers preserved:  {all_stabilized}")


                    ft_details, is_ft = check_fault_tolerance(circuit_str, qubits, ancillas, distance)

                    print(f"  ✓ Circuit generated successfully - FT check: {is_ft}")

                    score = ft_score(circuit_str, qubits, ancillas, distance, 1.0)
                    print(f"   FT score: {score}")
                    # generated_candidates.append({
                    #     "circuit": circuit_str,
                    #     "ft_score": score
                    # })

                    all_true = all([all_stabilized, is_ft])
                else:
                    circuit_str = None
                    # ancilla = None
                    is_ft = None
                    ft_details = None
                    score = None
                    stab_results = None
                    all_stabilized = None
                    all_true = None
                    end_time = datetime.now()
                    print("  ✗ Failed to generate circuit")
                    
            except Exception as e:
                circuit_str = None
                # ancilla = None
                is_ft = None
                ft_details = None
                score = None
                stab_results = None
                all_stabilized = None
                all_true = None
                end_time = datetime.now()
                print(f"  ✗ Error: {e}")

            runtime_seconds = None
            if start_time and end_time:
                runtime_seconds = (end_time - start_time).total_seconds()
                        

            #output all of the circuits instead of the most valid one (just the score and the circuit, not the other stuff)
            # best = {
            #     "circuit": circuit_str,
            #     "ft_score": score,
            #     "ft_check": is_ft,
            #     "all_stabilized": all_stabilized,
            #     "stabilizer_details": stab_results,
            #     "ALL TRUE": all_true
            # }
            # result = {
            #     "code_name": entry["source_code"],
            #     "original_score": orig_ft_score,
            #     "start_time": start_time.isoformat() if start_time else None,
            #     "end_time": end_time.isoformat() if end_time else None,
            #     "runtime_seconds": runtime_seconds,
            #     "best_output": best
            #     # "generated_circuits": generated_candidates
            # }
            # Best output
            best = {
                "circuit": circuit_str,
                "ft_score": score, 
                "ft_check": is_ft,
                "all_stabilized": all_stabilized,
                "stabilizer_details": stab_results,
                "ALL TRUE": all_true
            }

            result = {
                "code_name": entry["source_code"],
                "original_score": orig_ft_score,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "runtime_seconds": runtime_seconds,
                "best_output": best,
                "generated_circuits": all_candidates  # <--- all intermediate circuits with FT scores
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
        default="data/generated_ft_circuits_cordelia.json",
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
