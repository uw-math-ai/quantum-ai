import stim

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def count_volume(circuit):
    # Volume is total number of gates in the volume gate set
    # The prompt defines volume as total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)
    # We will just count all operations that are gates.
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instr.targets_copy()) // 2
            else:
                count += len(instr.targets_copy())
    return count

def main():
    with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/agent_files/baseline.stim", "r") as f:
        baseline_text = f.read()
    
    baseline_circuit = stim.Circuit(baseline_text)
    base_cx = count_cx(baseline_circuit)
    base_vol = count_volume(baseline_circuit)
    
    print(f"Baseline CX: {base_cx}")
    print(f"Baseline Volume: {base_vol}")
    
    with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/agent_files/stabilizers.txt", "r") as f:
        lines = f.readlines()
    
    stabilizers = [line.strip() for line in lines if line.strip()]
    
    # Attempt synthesis
    print("Synthesizing...")
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        synth_circuit = tableau.to_circuit("h_s_cx_mcz_phase_gadget") # Use standard method
        
        synth_cx = count_cx(synth_circuit)
        synth_vol = count_volume(synth_circuit)
        
        print(f"Synthesized CX: {synth_cx}")
        print(f"Synthesized Volume: {synth_vol}")
        
        if synth_cx < base_cx or (synth_cx == base_cx and synth_vol < base_vol):
            print("SUCCESS: Synthesized circuit is better.")
            with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/agent_files/candidate.stim", "w") as f:
                f.write(str(synth_circuit))
        else:
            print("FAILURE: Synthesized circuit is NOT better.")
            
            # Try method='elimination' if available or just to_circuit() without arguments often defaults to Gaussian elimination
            print("Trying default synthesis...")
            synth_circuit_2 = tableau.to_circuit()
            synth_cx_2 = count_cx(synth_circuit_2)
            synth_vol_2 = count_volume(synth_circuit_2)
            print(f"Synthesized 2 CX: {synth_cx_2}")
            print(f"Synthesized 2 Volume: {synth_vol_2}")

            if synth_cx_2 < base_cx or (synth_cx_2 == base_cx and synth_vol_2 < base_vol):
                 print("SUCCESS: Synthesized circuit 2 is better.")
                 with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/agent_files/candidate.stim", "w") as f:
                    f.write(str(synth_circuit_2))

    except Exception as e:
        print(f"Error during synthesis: {e}")

if __name__ == "__main__":
    main()
