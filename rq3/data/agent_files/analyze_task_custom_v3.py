import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
    return count

def analyze():
    # Load baseline from file
    try:
        with open("my_baseline.stim", "r") as f:
            baseline_text = f.read()
            baseline = stim.Circuit(baseline_text)
            print(f"Baseline loaded. CX count: {count_cx(baseline)}")
    except Exception as e:
        print(f"Error loading baseline: {e}")

    # Load stabilizers
    stabilizers = []
    try:
        with open("my_stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(stabilizers)} stabilizers.")
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    if not stabilizers:
        print("No stabilizers found.")
        return

    n_qubits = len(stabilizers[0])
    print(f"Stabilizer length (n_qubits): {n_qubits}")

    # Create Tableau
    try:
        # Convert strings to PauliStrings
        stabilizers_ps = [stim.PauliString(s) for s in stabilizers]
        t = stim.Tableau.from_stabilizers(stabilizers_ps, allow_redundant=True, allow_underconstrained=True)
        print(f"Tableau valid. Size: {len(t)}")
        
        # Method 1: Graph state synthesis
        c_graph = t.to_circuit(method="graph_state")
        print(f"Graph state synthesis CX count: {count_cx(c_graph)}")
        with open("candidate_graph.stim", "w") as f:
            f.write(str(c_graph))
        
        # Method 2: Standard synthesis
        c_std = t.to_circuit(method="elimination")
        print(f"Elimination synthesis CX count: {count_cx(c_std)}")
        with open("candidate_elimination.stim", "w") as f:
            f.write(str(c_std))

    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    analyze()
