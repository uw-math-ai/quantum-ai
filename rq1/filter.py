import json
import argparse

def parse_circuit(circuit_str):
    """Compute total gates and weighted gate count (H=1, CX/CZ=2)"""
    total_gates = 0
    weighted_gates = 0

    if not circuit_str.strip():
        return 0, 0

    for line in circuit_str.strip().split("\n"):
        tokens = line.split()
        if not tokens:
            continue
        gate = tokens[0].upper()
        qubit_tokens = tokens[1:]

        # Try to parse qubit indices as integers
        qubits = []
        for q in qubit_tokens:
            try:
                qubits.append(int(q))
            except ValueError:
                # Skip non-integer tokens
                continue

        if gate in {"H", "S"}:
            n_gates = len(qubits)
            total_gates += n_gates
            weighted_gates += n_gates * 1
        elif gate in {"CX", "CZ"}:
            n_gates = len(qubits) // 2  # Each 2-qubit gate uses 2 indices
            total_gates += n_gates
            weighted_gates += n_gates * 2
        else:
            # Unknown gate, count as 1
            total_gates += 1
            weighted_gates += 1

    return total_gates, weighted_gates

def compute_stabilizer_weights(generators):
    if not generators:
        return 0.0, 0
    weights = [sum(1 for c in g.upper() if c in {"X", "Y", "Z"}) for g in generators]
    avg_weight = sum(weights) / len(weights)
    max_weight = max(weights)
    return avg_weight, max_weight

def main(benchmarks_file, results_file, output_file):
    # Load benchmarks
    with open(benchmarks_file) as f:
        benchmarks = json.load(f)
    benchmark_map = {b.get("name", ""): b for b in benchmarks}

    # Load results JSON
    with open(results_file) as f:
        data = json.load(f)
    
    circuits = data.get("results", [])
    if not circuits:
        raise ValueError("No 'results' list found in results JSON")

    output_data = []

    for circuit_entry in circuits:
        code_name = circuit_entry.get("code_name", "")
        circuit_str = circuit_entry.get("circuit", "")

        # Skip if circuit is missing or empty
        if not circuit_str:
            print(f"Skipping {code_name}: empty circuit")
            continue

        benchmark = benchmark_map.get(code_name, {})

        # Features from benchmarks
        logical_qubits = benchmark.get("logical_qubits", None)
        physical_qubits = benchmark.get("physical_qubits", None)
        n_stabilizers = len(benchmark.get("generators", []))
        distance = benchmark.get("d", None)

        # Circuit features
        total_gates, weighted_gates = parse_circuit(circuit_str)

        # Stabilizer weights
        avg_stab_weight, max_stab_weight = compute_stabilizer_weights(benchmark.get("generators", []))

        # Build output entry
        out_entry = {
            "code_name": code_name,
            "success_rate": circuit_entry.get("success_rate", None),
            "elapsed_seconds": circuit_entry.get("elapsed_seconds", None),
            "logical_qubits": logical_qubits,
            "physical_qubits": physical_qubits,
            "n_stabilizers": n_stabilizers,
            "distance": distance,
            "total_gates": total_gates,
            "weighted_gate_count": weighted_gates,
            "avg_stabilizer_weight": avg_stab_weight,
            "max_stabilizer_weight": max_stab_weight
        }

        output_data.append(out_entry)

    # Write output JSON
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Feature extraction complete. {len(output_data)} entries written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute circuit features from benchmarks and results")
    parser.add_argument("benchmarks_file", help="Path to benchmarks.json")
    parser.add_argument("results_file", help="Path to circuit results JSON")
    parser.add_argument("output_file", help="Path to output JSON file")
    args = parser.parse_args()

    main(args.benchmarks_file, args.results_file, args.output_file)