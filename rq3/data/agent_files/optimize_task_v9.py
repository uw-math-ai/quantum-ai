import stim

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instruction.targets_copy()) // 2
            else:
                count += len(instruction.targets_copy())
    return count

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = True
    failed_count = 0
    for stab_str in stabilizers:
        # Convert string to PauliString
        pauli = stim.PauliString(stab_str)
        if sim.peek_observable_expectation(pauli) != 1:
            preserved = False
            failed_count += 1
    return preserved, failed_count

def main():
    # Load baseline
    with open("baseline_task_v9.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    # Load stabilizers
    stabilizers = []
    with open("stabilizers_task_v9.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(line)
    
    b_cx = count_cx(baseline)
    b_vol = count_volume(baseline)
    print(f"Baseline CX count: {b_cx}")
    print(f"Baseline Volume: {b_vol}")
    
    is_valid, failed = check_stabilizers(baseline, stabilizers)
    print(f"Baseline preserves stabilizers: {is_valid} (failed: {failed})")
    
    # Try simple synthesis
    try:
        stim_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_underconstrained=True, allow_redundant=True)
        synthesized = tableau.to_circuit("graph_state")
        
        # Count CZs
        cz_count = 0
        for op in synthesized:
            if op.name == "CZ":
                cz_count += len(op.targets_copy()) // 2
        print(f"Synthesized CZ count: {cz_count}")
        
        s_cx = count_cx(synthesized)
        s_vol = count_volume(synthesized)
        print(f"Synthesized CX count: {s_cx}")
        print(f"Synthesized Volume: {s_vol}")
        
        is_valid_s, failed_s = check_stabilizers(synthesized, stabilizers)
        print(f"Synthesized preserves stabilizers: {is_valid_s} (failed: {failed_s})")
        
        if is_valid_s:
            if s_cx < b_cx or (s_cx == b_cx and s_vol < b_vol):
                print("Synthesis is better!")
                with open("candidate_v9.stim", "w") as f:
                    f.write(str(synthesized))
            else:
                print("Synthesis is valid but NOT better.")
        else:
            print("Synthesis is NOT valid.")
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    main()
