import json
import os
import sys
import argparse
import time
from datetime import datetime

# Add tools directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))

from agent import generate_state_prep
from check_stabilizers import check_stabilizers


def generate_circuits_from_benchmarks(
    benchmarks_path: str,
    output_path: str | None = None,
    model: str = "claude-sonnet-4.5",
    attempts: int = 3,
    timeout: int = 60
) -> list[dict]:
    """
    Generate state preparation circuits for all stabilizer groups in benchmarks.
    
    Args:
        benchmarks_path: Path to the benchmarks JSON file
        output_path: Path to save the output JSON file.
            If None, auto-generates as data/<model>/<YYMMdd.HHmm>.json
        model: The model to use for generation (default: claude-sonnet-4.5)
        attempts: Number of attempts for each circuit generation
        timeout: Timeout in seconds for each generation
    
    Returns:
        List of dictionaries with code_name, generators, and circuit
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%y%m%d.%H%M")
        output_dir = os.path.join(".", "data", model)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{timestamp}.json")

    with open(benchmarks_path, 'r') as f:
        benchmarks = json.load(f)
    
    metadata = {
        "benchmarks_path": benchmarks_path,
        "model": model,
        "attempts": attempts,
        "timeout": timeout,
        "started_at": datetime.now().isoformat(),
    }
    results = []
    
    try:
        count = 0
        for i, benchmark in enumerate(benchmarks):
            code_name = benchmark.get("name")
            generators = benchmark.get("generators")
            count += 1
            
            if not code_name or not generators:
                print(f"[{i+1}/{len(benchmarks)}] Skipping entry with missing name or generators")
                continue
            
            print(f"[{i+1}/{len(benchmarks)}] Generating circuit for: {code_name}")
            # print(f"  Generators: {generators}")
            
            start_time = time.time()
            try:
                circuit = generate_state_prep(
                    stabilizers=generators,
                    model=model,
                    attempts=attempts,
                    timeout=timeout,
                )
                
                if circuit is not None:
                    circuit_str = str(circuit)
                    stab_results = check_stabilizers(circuit_str, generators)
                    preserved = sum(1 for ok in stab_results.values() if ok)
                    total = len(stab_results)
                    print(f"  ✓ Circuit generated — stabilizers preserved: {preserved}/{total}")
                else:
                    circuit_str = None
                    stab_results = None
                    preserved = 0
                    total = len(generators)
                    print(f"  ✗ Failed to generate circuit")
                    
            except Exception as e:
                circuit_str = None
                stab_results = None
                preserved = 0
                total = len(generators)
                print(f"  ✗ Error: {e}")
            
            elapsed_seconds = round(time.time() - start_time, 2)
            print(f"  ⏱ Elapsed: {elapsed_seconds}s")

            result = {
                "code_name": code_name,
                "circuit": circuit_str,
                "stabilizes": stab_results,
                "preserved": preserved,
                "total": total,
                "success_rate": preserved / total,
                "elapsed_seconds": elapsed_seconds
            }
            results.append(result)
            
            # Save intermediate results after each generation
            output = {"metadata": metadata, "results": results}
            with open(output_path, 'w') as f:
                json.dump(output, f, indent=4)
            print(f"  Saved intermediate results to {output_path}")
    finally:
        metadata["finished_at"] = datetime.now().isoformat()
        output = {"metadata": metadata, "results": results}
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

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
        default="../data/benchmarks.json",
        help="Path to benchmarks JSON file"
    )
    parser.add_argument(
        "--output", 
        default=None,
        help="Path to output JSON file (default: ./data/<model>/<YYMMdd.HHmm>.json)"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4.5",
        help="Model to use for generation (default: claude-sonnet-4.5)"
    )
    parser.add_argument(
        "--attempts", 
        type=int, 
        default=10,
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
        model=args.model,
        attempts=args.attempts,
        timeout=args.timeout
    )


if __name__ == "__main__":
    main()
