import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instr.targets_copy()) // 2
            else:
                count += len(instr.targets_copy())
    return count

def main():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\baseline_new.stim", "r") as f:
            baseline_text = f.read()
        
        baseline_circuit = stim.Circuit(baseline_text)
        base_cx = count_cx(baseline_circuit)
        base_vol = count_volume(baseline_circuit)
        
        print(f"Baseline CX: {base_cx}")
        print(f"Baseline Volume: {base_vol}")
        
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\stabilizers.txt", "r") as f:
            lines = f.readlines()
        
        stabilizers = [stim.PauliString(line.strip()) for line in lines if line.strip()]
        
        print("Synthesizing...")
        
        # Method 1: Standard synthesis
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        synth_circuit = tableau.to_circuit("elimination")
        
        synth_cx = count_cx(synth_circuit)
        synth_vol = count_volume(synth_circuit)
        
        print(f"Synthesized (Elimination) CX: {synth_cx}")
        print(f"Synthesized (Elimination) Volume: {synth_vol}")
        
        best_circuit = synth_circuit
        best_cx = synth_cx
        best_vol = synth_vol

        # Method 2: Graph state synthesis (if applicable)
        # Often 'elimination' does this well, but let's check the graph state approach explicitly if needed
        # But 'from_stabilizers' already finds a stabilizer state.
        
        # Check against baseline
        if best_cx < base_cx or (best_cx == base_cx and best_vol < base_vol):
            print("SUCCESS: Synthesized circuit is better.")
            with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate.stim", "w") as f:
                f.write(str(best_circuit))
        else:
            print("FAILURE: Synthesized circuit is NOT better.")
            # Still save it for inspection
            with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate_failed.stim", "w") as f:
                f.write(str(best_circuit))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
