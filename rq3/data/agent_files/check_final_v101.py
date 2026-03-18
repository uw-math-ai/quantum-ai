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
    # Load candidate
    with open("candidate_v9.stim", "r") as f:
        candidate_text = f.read()
    try:
        candidate = stim.Circuit(candidate_text)
    except Exception as e:
        print(f"Candidate invalid: {e}")
        return
        
    # Check for forbidden instructions
    forbidden = ["M", "R", "RX", "RY", "RZ", "MPP", "MX", "MY", "MZ", "MR", "MRX", "MRY", "MRZ"]
    for op in candidate:
        if op.name in forbidden:
            print(f"Forbidden instruction found: {op.name}")
            return

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
    c_cx = count_cx(candidate)
    c_vol = count_volume(candidate)
    
    print(f"Baseline CX: {b_cx}, Vol: {b_vol}")
    print(f"Candidate CX: {c_cx}, Vol: {c_vol}")
    
    is_valid, failed = check_stabilizers(candidate, stabilizers)
    print(f"Candidate preserves stabilizers: {is_valid} (failed: {failed})")
    
    if is_valid:
        if c_cx < b_cx or (c_cx == b_cx and c_vol < b_vol):
            print("BETTER!")
        else:
            print("NOT BETTER!")

if __name__ == "__main__":
    main()
