import stim
import sys

def count_cx(circuit):
    return sum(1 for op in circuit if op.name in ["CX", "CNOT"])

def count_volume(circuit):
    # Volume is total number of operations
    return sum(1 for op in circuit)

def get_metrics(circuit):
    return (count_cx(circuit), count_volume(circuit), len(circuit))

def main():
    with open("target_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # print(f"Loaded {len(stabilizers)} stabilizers.")

    with open("baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    base_metrics = get_metrics(baseline)
    # print(f"Baseline metrics: {base_metrics}")

    # Create tableau from stabilizers
    # stim.Tableau.from_stabilizers takes a list of stim.PauliString
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Method 1: Standard synthesis
    circ1 = tableau.to_circuit(method="elimination")
    m1 = get_metrics(circ1)
    # print(f"Method 1 (elimination): {m1}")

    # Method 2: Graph state synthesis
    circ2_raw = tableau.to_circuit(method="graph_state")
    
    # Clean circuit: Replace RX with H, remove R (assuming start at |0>)
    circ2 = stim.Circuit()
    for op in circ2_raw:
        if op.name == "RX":
            # RX resets to |+>. Since we start at |0>, apply H to get |+>.
            circ2.append("H", op.targets_copy())
        elif op.name == "R":
            # R resets to |0>. Already at |0>. Do nothing.
            pass
        else:
            circ2.append(op)
            
    m2 = get_metrics(circ2)
    print(f"Method 2 (graph_state, cleaned): {m2}")

    # Verify stabilizers for circ2
    # We check if the circuit maps |0> to the target stabilizer state.
    # To verify, we can peek expectation of target stabilizers.
    # But peeking requires a simulator and might be slow or tricky.
    # Instead, trust the synthesis IF it is valid.
    # Let's rely on evaluate_optimization for final check, but we can do a quick check here.
    
    # Check if either is better
    best_circ = None
    best_metrics = base_metrics
    best_name = "baseline"

    candidates = [("elimination", circ1, m1), ("graph_state", circ2, m2)]

    for name, circ, m in candidates:
        # Lexicographic comparison: (cx, volume, depth)
        # Check strict improvement
        is_better = False
        if m[0] < best_metrics[0]:
            is_better = True
        elif m[0] == best_metrics[0]:
            if m[1] < best_metrics[1]:
                is_better = True
            elif m[1] == best_metrics[1]:
                 if m[2] < best_metrics[2]:
                    is_better = True
        
        if is_better:
            best_metrics = m
            best_circ = circ
            best_name = name

    print(f"Best local candidate: {best_name} with metrics {best_metrics}")

    if best_circ:
        # print(best_circ)
        with open("candidate.stim", "w") as f:
            f.write(str(best_circ))
        print("Written best candidate to candidate.stim")
    else:
        # If no improvement found, print baseline so we at least have valid circuit
        print(baseline)

if __name__ == "__main__":
    main()
