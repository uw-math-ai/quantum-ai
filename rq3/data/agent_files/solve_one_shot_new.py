import stim

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    # volume is total gate count in volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)
    # Approximate based on instructions
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
             # For 2 qubit gates, it counts as 1 op per pair?
             # The metric description says "total gate count".
             # Usually implies number of operations.
             if instr.name in ["CX", "CY", "CZ"]:
                 count += len(instr.targets_copy()) // 2
             else:
                 count += len(instr.targets_copy())
    return count

def main():
    # Load baseline
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    base_cx = count_cx(baseline)
    base_vol = get_volume(baseline)
    
    print(f"Baseline CX: {base_cx}")
    print(f"Baseline Volume: {base_vol}")
    
    # Load stabilizers
    stabilizers = []
    with open("target_stabilizers.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))
                
    # Create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize using graph state
    # method="graph_state" is usually optimal for CX count in stabilizer states
    try:
        new_circuit = tableau.to_circuit(method="graph_state")
        new_cx = count_cx(new_circuit)
        new_vol = get_volume(new_circuit)
        
        print(f"New CX: {new_cx}")
        print(f"New Volume: {new_vol}")
        
        if new_cx < base_cx or (new_cx == base_cx and new_vol < base_vol):
            print("Improvement found!")
            with open("candidate.stim", "w") as f:
                f.write(str(new_circuit))
        else:
            print("No improvement with graph_state.")
            
            # Try "elimination" method
            new_circuit_elim = tableau.to_circuit(method="elimination")
            elim_cx = count_cx(new_circuit_elim)
            elim_vol = get_volume(new_circuit_elim)
            print(f"Elimination CX: {elim_cx}")
            print(f"Elimination Volume: {elim_vol}")
            
            if elim_cx < base_cx:
                 print("Improvement found with elimination!")
                 with open("candidate.stim", "w") as f:
                    f.write(str(new_circuit_elim))
    except Exception as e:
        print(f"Error synthesizing: {e}")

if __name__ == "__main__":
    main()
