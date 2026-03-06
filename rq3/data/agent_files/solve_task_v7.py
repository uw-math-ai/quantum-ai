import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            if hasattr(instruction, "targets_copy"):
                 targets = instruction.targets_copy()
            else:
                 targets = instruction.targets
            count += len(targets) // 2
    return count

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return lines

def main():
    # Load baseline
    try:
        baseline = stim.Circuit.from_file("baseline_task_v7.stim")
        print(f"Baseline CX count: {count_cx(baseline)}")
        print(f"Baseline instructions: {len(baseline)}")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        # return - don't return, continue to synthesis if possible

    # Load stabilizers
    stabilizers = load_stabilizers("stabilizers_task_v7.txt")
    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Try synthesis with permutations
    best_cx = 999999
    best_circuit = None
    best_method = ""

    import random
    
    # Define strategies
    strategies = [
        ("original", lambda s: s),
        ("sorted_first", lambda s: sorted(s, key=lambda x: next((i for i, c in enumerate(x) if c in 'XYZ'), 999))),
        ("sorted_last", lambda s: sorted(s, key=lambda x: -next((i for i, c in enumerate(reversed(x)) if c in 'XYZ'), 999))),
        ("sorted_weight", lambda s: sorted(s, key=lambda x: sum(1 for c in x if c in 'XYZ'))),
        ("reverse", lambda s: list(reversed(s))),
    ]
    
    # Add random shuffles
    for i in range(20):
        strategies.append((f"shuffle_{i}", lambda s: random.sample(s, len(s))))

    for name, strategy in strategies:
        try:
            current_stabilizers = strategy(stabilizers)
            tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in current_stabilizers], allow_underconstrained=True, allow_redundant=True)
            
            # Try available methods
            methods = ["elimination"] # Add "graph_state" if valid
            
            for method in methods:
                try:
                    circuit = tableau.to_circuit(method=method)
                    cx = count_cx(circuit)
                    # print(f"Strategy {name} ({method}): {cx} CX")
                    
                    if cx < best_cx:
                        best_cx = cx
                        best_circuit = circuit
                        best_method = f"{name}-{method}"
                        print(f"New best: {cx} CX using {name} ({method})")
                except Exception as e:
                    # print(f"Method {method} failed for {name}: {e}")
                    pass
                    
        except Exception as e:
            print(f"Strategy {name} failed: {e}")

    print(f"Best CX found: {best_cx} (Method: {best_method})")
    
    if best_circuit:
        with open("candidate_circuit.stim", "w") as f:
            f.write(str(best_circuit))

if __name__ == "__main__":
    main()
