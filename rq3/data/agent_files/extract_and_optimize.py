import stim

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def get_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
             if instr.name in ["CX", "CY", "CZ"]:
                 count += len(instr.targets_copy()) // 2
             else:
                 count += len(instr.targets_copy())
    return count

def main():
    # Load baseline
    try:
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error reading baseline: {e}")
        return

    base_cx = count_cx(baseline)
    base_vol = get_volume(baseline)
    print(f"Baseline CX: {base_cx}")
    print(f"Baseline Volume: {base_vol}")

    # Extract stabilizers from baseline
    try:
        sim = stim.TableauSimulator()
        sim.do_circuit(baseline)
        tableau = sim.current_inverse_tableau().inverse() # Tableau of the state
        # Actually, sim.canonical_stabilizers() is better but stim doesn't have it directly on simulator?
        # tableau.to_stabilizers() gives generators.
        extracted_stabilizers = tableau.to_stabilizers()
        print(f"Extracted {len(extracted_stabilizers)} stabilizers from baseline.")
        
        # Check if they look like the prompt
        print("First extracted stabilizer:", extracted_stabilizers[0])
        
    except Exception as e:
        print(f"Error extracting stabilizers: {e}")
        return

    # Synthesize from extracted stabilizers
    try:
        # Use graph_state method
        new_circuit = tableau.to_circuit(method="graph_state")
        new_cx = count_cx(new_circuit)
        new_vol = get_volume(new_circuit)
        
        print(f"Graph State CX: {new_cx}")
        print(f"Graph State Volume: {new_vol}")
        
        if new_cx < base_cx or (new_cx == base_cx and new_vol < base_vol):
            print("Improvement found!")
            with open("candidate_derived.stim", "w") as f:
                f.write(str(new_circuit))
        else:
            print("No improvement with graph_state.")
            
            # Try elimination
            new_circuit_elim = tableau.to_circuit(method="elimination")
            elim_cx = count_cx(new_circuit_elim)
            elim_vol = get_volume(new_circuit_elim)
            print(f"Elimination CX: {elim_cx}")
            
            if elim_cx < base_cx:
                print("Improvement found with elimination!")
                with open("candidate_derived.stim", "w") as f:
                    f.write(str(new_circuit_elim))

    except Exception as e:
        print(f"Error synthesizing: {e}")

if __name__ == "__main__":
    main()
