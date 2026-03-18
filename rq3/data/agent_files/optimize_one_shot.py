import stim
import sys

def solve():
    print("Loading data...")
    try:
        with open("C:/Users/anpaz/Repos/quantum-ai/rq3/stabilizers.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        with open("C:/Users/anpaz/Repos/quantum-ai/rq3/baseline.stim", "r") as f:
            baseline_circuit = stim.Circuit(f.read())
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    print(f"Loaded {len(stabilizers)} stabilizers.")
    print(f"Baseline circuit: {baseline_circuit.num_qubits} qubits, {len(baseline_circuit)} instructions.")

    # Calculate baseline metrics
    baseline_cx = baseline_circuit.num_2_qubit_gates()
    # Volume is total gates. Stim doesn't have a direct method for volume in the sense of the problem (gate count), but usually len(circuit) is close if flattened. 
    # But wait, instructions like 'CX 0 1 2 3' count as 1 instruction but 2 gates.
    # We need to count gates properly.
    
    def count_metrics(circuit):
        cx_count = 0
        volume = 0
        for instruction in circuit:
            if instruction.name in ["CX", "CNOT"]:
                # The length of targets is 2 * gate_count for 2-qubit gates
                cx_count += len(instruction.targets) // 2
                volume += len(instruction.targets) // 2
            elif instruction.name in ["H", "S", "X", "Y", "Z", "I", "SQRT_X", "SQRT_Y", "SQRT_Z", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
                 volume += len(instruction.targets)
            # Add other gates if necessary
        return cx_count, volume

    base_cx, base_vol = count_metrics(baseline_circuit)
    print(f"Baseline metrics: CX={base_cx}, Vol={base_vol}")

    # Attempt synthesis using Tableau
    print("Attempting synthesis from stabilizers...")
    try:
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
        synthesized_circuit = tableau.to_circuit()
        
        syn_cx, syn_vol = count_metrics(synthesized_circuit)
        print(f"Synthesized metrics: CX={syn_cx}, Vol={syn_vol}")
        
        if syn_cx < base_cx or (syn_cx == base_cx and syn_vol < base_vol):
            print("Synthesis produced a better circuit!")
            with open("C:/Users/anpaz/Repos/quantum-ai/rq3/candidate.stim", "w") as f:
                f.write(str(synthesized_circuit))
        else:
            print("Synthesis was not better.")
            # If synthesis is worse, we might just try to output the baseline as a fallback, 
            # or try to optimize the baseline.
            # Let's try to optimize the baseline using a graph state approach if possible?
            pass

    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    solve()
