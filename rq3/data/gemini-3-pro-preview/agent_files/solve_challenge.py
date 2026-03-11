import stim
import os

def solve():
    base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files"
    
    # Read files
    with open(os.path.join(base_dir, "baseline.stim"), "r") as f:
        baseline_text = f.read()
    
    with open(os.path.join(base_dir, "target_stabilizers.txt"), "r") as f:
        stabilizers_text = [l.strip() for l in f if l.strip()]

    # Parse baseline
    baseline = stim.Circuit(baseline_text)
    print(f"Baseline gates: {baseline.num_gates}")
    print(f"Baseline 2q gates: {baseline.num_2q_gates}")

    # Create tableau from stabilizers
    try:
        t = stim.Tableau.from_stabilizers(stabilizers_text, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Method 1: Graph state synthesis
    # This creates a circuit with H, S, CZ, CX (maybe), etc.
    # We want to minimize CX count.
    # Graph state synthesis primarily uses CZs.
    c_graph = t.to_circuit(method="graph_state")
    
    # Clean up RX if present (replace RX with H, assuming start state |0>)
    # But wait, RX resets to |+>. If we start at |0>, H does that.
    # If the circuit STARTS with RX, we can just replace with H.
    # If RX is in the middle, it is a reset.
    # The baseline has no resets. We should assume we start from |0>.
    # So 'RX' instruction at the beginning is just 'H'.
    # If 'RX' is later, it's a reset.
    
    # Let's post-process the circuit
    new_circuit = stim.Circuit()
    for instruction in c_graph:
        if instruction.name == "RX":
            # Replace RX target with H target
            for target in instruction.targets_copy():
                new_circuit.append("H", [target])
        else:
            new_circuit.append(instruction)

    print("\n--- Candidate 1 (Graph State) ---")
    print(new_circuit)
    
    # Method 2: Elimination based synthesis
    c_elim = t.to_circuit(method="elimination")
    print("\n--- Candidate 2 (Elimination) ---")
    print(c_elim)

if __name__ == "__main__":
    solve()
