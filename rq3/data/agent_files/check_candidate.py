import stim

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def calculate_volume(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instr.targets_copy()) // 2
            else:
                count += len(instr.targets_copy())
    return count

def check():
    circuit = stim.Circuit.from_file("candidate.stim")
    
    # Load stabilizers
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Check expectation
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
            
    print(f"Candidate preserves {preserved}/{len(stabilizers)} stabilizers.")
    
    cx = count_cx(circuit)
    vol = calculate_volume(circuit)
    print(f"Candidate metrics: cx_count={cx}, volume={vol}")
    
    # Compare with baseline (hardcoded from previous run)
    base_cx = 154
    base_vol = 163
    
    if preserved == len(stabilizers):
        print("Candidate is VALID.")
        if (cx < base_cx) or (cx == base_cx and vol < base_vol):
            print("Candidate is BETTER.")
        else:
            print("Candidate is NOT better.")
    else:
        print("Candidate is INVALID.")

if __name__ == "__main__":
    check()
