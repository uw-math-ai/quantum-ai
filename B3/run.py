import json
import os
import sys
import argparse
import stim
from copy import deepcopy
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PROMPT = os.path.join(SCRIPT_DIR, "prompts", "default_prompt.txt")
DEFAULT_BENCHMARKS = os.path.join(SCRIPT_DIR, "..", "data", "circuit_dataset.jsonl")

# Add tools directory to path for imports
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', 'tools'))


from datetime import datetime
from agent import CircuitParam, define_tool, generate_ft_state_prep, prompt_agent
from validate_ft_circuits import check_syndrome_extraction_ft
from check_error_propagation import check_fault_tolerance, ft_score
from check_stabilizers import check_stabilizers

def generate_circuits_from_data(
    benchmarks_path: str,
    output_path: str|None = None,
    model: str = "gpt-5.2-codex",
    harness: str = "openai",
    attempts: int = 3,
    timeout: int = 60,
    prompt_file: str = "prompts/default_prompt.txt"
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
    if output_path is None:
        timestamp = datetime.now().strftime("%y%m%d.%H%M")
        output_dir = os.path.join(SCRIPT_DIR, "data", model)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{timestamp}.json")

    started_at = datetime.now()
    results = []
    with open(benchmarks_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            source_code = entry["source_code"]
            distance = entry["d"]
            qubits = entry["permutation"]
            input_stabilizers = entry["input_stabilizers"]
            output_circuit = entry["output_circuit"]
            ancillas = []
            all_candidates = []
            start_time = None
            end_time = None

            # Compute FT score of the original (non-FT) circuit
            orig_ancillas = []
            clean_circuit = output_circuit.replace("\\n", "\n")
            orig_ft_score = ft_score(clean_circuit, qubits, orig_ancillas, distance)
            print(f"Original FT score: {orig_ft_score}")
            try:
                start_time = datetime.now()

                circuit_results, all_candidates = generate_ft_state_prep(
                    stabilizers=input_stabilizers,
                    non_ft_circuit = output_circuit,
                    distance = distance,
                    attempts=attempts,
                    timeout=timeout,
                    model=model,
                    harness=harness,
                    prompt_file=prompt_file
                )
                end_time = datetime.now()

                # If no final result but we have validated candidates, use the latest one
                if circuit_results is None and all_candidates:
                    latest = all_candidates[-1]
                    print(f"  ⚠ Timed out, falling back to latest verified circuit (ft_score={latest['ft_score']})")
                    circuit_results = {"circuit": stim.Circuit(latest["circuit"])}

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

                    score = ft_score(circuit_str, qubits, ancillas, distance)
                    print(f"   FT score: {score}")

                    all_true = all([all_stabilized, is_ft])
                else:
                    circuit_str = None
                    is_ft = None
                    ft_details = None
                    score = None
                    stab_results = None
                    all_stabilized = None
                    all_true = None
                    end_time = datetime.now()
                    print("  ✗ Failed to generate circuit")
                    
            except Exception as e:
                end_time = datetime.now()
                print(f"  ✗ Error: {e}")

                # If we have validated candidates, fall back to the latest one
                if all_candidates:
                    latest = all_candidates[-1]
                    print(f"  ⚠ Falling back to latest verified circuit (ft_score={latest['ft_score']})")
                    circuit_obj = stim.Circuit(latest["circuit"])
                    circuit_str = str(circuit_obj)

                    used_qubits = set()
                    for inst in circuit_obj:
                        for t in inst.targets_copy():
                            if hasattr(t, "value"):
                                used_qubits.add(t.value)

                    data_qubits = set(qubits)
                    ancillas = sorted(list(used_qubits - data_qubits))

                    stab_results = check_stabilizers(circuit_str, input_stabilizers)
                    all_stabilized = all(stab_results.values())
                    ft_details, is_ft = check_fault_tolerance(circuit_str, qubits, ancillas, distance)
                    score = ft_score(circuit_str, qubits, ancillas, distance)
                    all_true = all([all_stabilized, is_ft])
                    print(f"   FT score: {score}, stabilizers: {all_stabilized}, FT: {is_ft}")
                else:
                    circuit_str = None
                    is_ft = None
                    ft_details = None
                    score = None
                    stab_results = None
                    all_stabilized = None
                    all_true = None
                    all_candidates = []

            runtime_seconds = None
            if start_time and end_time:
                runtime_seconds = (end_time - start_time).total_seconds()

            # Annotate every candidate with whether it preserves all stabilizers.
            # (Folded in from the former 1.add_stabilized_check.py post-processing
            # script so a single run produces fully-annotated output.)
            for cand in all_candidates:
                cand_circuit = cand.get("circuit")
                if cand_circuit is None:
                    cand["all_stabilized"] = None
                    continue
                try:
                    cand_stab = check_stabilizers(cand_circuit, input_stabilizers)
                    cand["all_stabilized"] = all(cand_stab.values())
                except Exception as e:
                    print(f"  ⚠ Error checking stabilizers for candidate in '{source_code}': {e}")
                    cand["all_stabilized"] = None

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
            output = {
                "metadata": {
                    "benchmarks_path": benchmarks_path,
                    "prompt_path": prompt_file,
                    "model": model,
                    "attempts": attempts,
                    "timeout": timeout,
                    "started_at": started_at.isoformat(),
                    "finished_at": datetime.now().isoformat()
                },
                "results": results
            }
            with open(output_path, 'w') as f:
                json.dump(output, f, indent=4)
            print(f"  Saved intermediate results to {output_path}")


        
    print(f"\nGeneration complete. {len(results)} circuits saved to {output_path}")
    return results


# ---------------------------------------------------------------------------
# Optional analysis (folded in from the former data_cleaning.py and
# data/analysis/build_cleaned2.py scripts). Enabled with --analyze; logic is
# unchanged, just parameterized by the run's output file instead of hardcoded
# file lists.
# ---------------------------------------------------------------------------

def clean_ft_results(file_path: str, output_path: str) -> None:
    """Determine how often the model selected the truly-best circuit
    (highest ft_score among all-stabilized candidates) as its best_output."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    cleaned_results = []
    temp_results = []

    num_correct = 0
    num_null = 0
    for result in data.get("results", []):
        code_name = result.get("code_name", "Unknown")
        results = {}
        best = result.get("best_output")
        if best.get("circuit") is not None:
            best_output_og = best.get("circuit")
            best_ft_score_og = best.get("ft_score")
            best_all_stabilized_og = best.get("all_stabilized")
            best_output = best.get("circuit")
            best_ft_score = best.get("ft_score")
            best_all_stabilized = best.get("all_stabilized")

            generated_circuits = result.get("generated_circuits", [])
            for circuit in generated_circuits:
                if (circuit.get("all_stabilized") == True and circuit.get("ft_score") > best_ft_score) or (circuit.get("all_stabilized") == True and best_all_stabilized == False):
                    best_output = circuit
                    best_ft_score = circuit.get("ft_score")
                    best_all_stabilized = circuit.get("all_stabilized")
            if best_output_og == best_output:
                num_correct += 1
                results = {
                    "code_name": code_name,
                    "correct": True
                }
            else:
                results = {
                    "code_name": code_name,
                    "correct": False,
                    "best_output_og": best_output_og,
                    "best_ft_score_og": best_ft_score_og,
                    "best_all_stabilized_og": best_all_stabilized_og,
                    "new_best_output": best_output
                }

            temp_results.append(results)
        else:
            num_null += 1
            results = {
                "code_name": code_name,
                "correct": False,
                "reason": "No circuit found"
            }
            temp_results.append(results)

    overall_accuracy = {
        "num_correct": num_correct,
        "num_null": num_null,
        "total (including null circuits)": len(data.get("results")),
        "incorrect": len(data.get("results")) - num_correct - num_null,
        "accuracy": num_correct / len(data.get("results")) if data.get("results") else 0.0,
        "accuracy (excluding null circuits)": num_correct / (len(data.get("results")) - num_null) if (len(data.get("results")) - num_null) > 0 else 0.0
    }

    cleaned_results.append(overall_accuracy)
    cleaned_results.append(temp_results)
    with open(output_path, 'w') as f:
        json.dump({"cleaned_results": cleaned_results}, f, indent=4)

    print(f"Cleaned results saved to {output_path}")


def build_raw_best_lookup(raw_path: Path) -> dict[str, dict]:
    with raw_path.open() as f:
        payload = json.load(f)

    best_lookup: dict[str, dict] = {}
    for result in payload.get("results", []):
        if not isinstance(result, dict):
            continue

        code_name = result.get("code_name")
        if not code_name:
            continue

        candidates: list[dict] = []
        best_output = result.get("best_output")
        if isinstance(best_output, dict):
            candidates.append(best_output)

        for candidate in result.get("generated_circuits", []):
            if isinstance(candidate, dict):
                candidates.append(candidate)

        valid_candidates = [
            candidate
            for candidate in candidates
            if candidate.get("all_stabilized") is True and candidate.get("ft_score") is not None
        ]
        if not valid_candidates:
            continue

        best_lookup[code_name] = max(valid_candidates, key=lambda candidate: candidate["ft_score"])

    return best_lookup


def build_cleaned2_payload(cleaned_path: Path, raw_path: Path) -> dict:
    with cleaned_path.open() as f:
        cleaned_payload = json.load(f)
    raw_best_lookup = build_raw_best_lookup(raw_path)

    cleaned2_payload = deepcopy(cleaned_payload)
    rebuilt_results: list = []

    for item in cleaned_payload.get("cleaned_results", []):
        if not isinstance(item, list):
            rebuilt_results.append(item)
            continue

        rebuilt_entries: list[dict] = []
        for entry in item:
            if not isinstance(entry, dict):
                rebuilt_entries.append(entry)
                continue

            if entry.get("correct") is False:
                rebuilt_entries.append(entry)
                continue

            code_name = entry.get("code_name")
            best_candidate = raw_best_lookup.get(code_name)
            if best_candidate is None:
                rebuilt_entries.append(entry)
                continue

            rebuilt_entry = deepcopy(entry)
            rebuilt_entry["new_best_output"] = {
                key: value
                for key, value in best_candidate.items()
                if key in {"circuit", "ft_score", "all_stabilized", "preserved_stabilizers", "ft_check", "stabilizer_details", "ALL TRUE"}
            }
            rebuilt_entries.append(rebuilt_entry)

        rebuilt_results.append(rebuilt_entries)

    cleaned2_payload["cleaned_results"] = rebuilt_results
    return cleaned2_payload


def run_analysis(output_path: str) -> None:
    """Run the cleaned/cleaned2 selection-accuracy analysis on a generation
    output file, writing results next to it under a cleaned/ subfolder."""
    out = Path(output_path)
    cleaned_dir = out.parent / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    cleaned_path = cleaned_dir / f"cleaned_{out.name}"
    clean_ft_results(str(out), str(cleaned_path))

    cleaned2_payload = build_cleaned2_payload(cleaned_path, out)
    cleaned2_path = cleaned_dir / f"cleaned2_{out.name}"
    with cleaned2_path.open("w") as f:
        json.dump(cleaned2_payload, f, indent=2)
        f.write("\n")
    print(f"Created {cleaned2_path}")


# To run this script, use the following command line format:
# python generate_state_prep_circuits.py --benchmarks data/benchmarks.json --output data/generated_circuits.json --attempts 3 --timeout 60
def main():
    parser = argparse.ArgumentParser(
        description="Generate fault-tolerant circuits for all circuits"
    )
    parser.add_argument(
        "--benchmarks",
        default=DEFAULT_BENCHMARKS,
        help="Path to benchmarks JSONL file (default: <script dir>/../data/circuit_dataset.jsonl)"
    )
    parser.add_argument(
        "--output", 
        default=None,
        help="Path to output JSON file (default: ./data/<model>/<YYMMdd.HHmm>.json)"
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
    parser.add_argument(
        "--model",
        default="gpt-5.2-codex",
        help="Model to use for generation (default: gpt-5.2-codex)"
    )
    parser.add_argument(
        "--harness",
        choices=("openai", "anthropic", "copilot"),
        default="openai",
        help="Provider harness to use (default: openai)"
    )
    parser.add_argument(
        "--prompt-file",
        default=DEFAULT_PROMPT,
        help="Path to the prompt template file (default: <script dir>/prompts/default_prompt.txt)"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="After generation, run the selection-accuracy analysis "
             "(writes cleaned_/cleaned2_ files next to the output)"
    )

    args = parser.parse_args()

    # Resolve the output path up front when analysis is requested so we know
    # which file to analyze. Mirrors generate_circuits_from_data's own
    # auto-naming exactly, so behaviour is unchanged.
    output_path = args.output
    if args.analyze and output_path is None:
        timestamp = datetime.now().strftime("%y%m%d.%H%M")
        output_dir = os.path.join(SCRIPT_DIR, "data", args.model)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{timestamp}.json")

    generate_circuits_from_data(
        benchmarks_path=args.benchmarks,
        output_path=output_path,
        model=args.model,
        harness=args.harness,
        attempts=args.attempts,
        timeout=args.timeout,
        prompt_file=args.prompt_file
    )

    if args.analyze:
        run_analysis(output_path)


if __name__ == "__main__":
    main()
