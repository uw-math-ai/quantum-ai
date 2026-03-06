import stim

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def calculate_volume(circuit):
    # Volume is total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)
    # Basically all gates except efficient Paulis? Or all gates?
    # The prompt says: "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
    # Usually this means all operations.
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            # For 2-qubit gates, stim lists targets in pairs.
            # For 1-qubit gates, it lists targets individually.
            # The "gate count" usually refers to the number of operations applied to qubits.
            # So a "CX 0 1 2 3" counts as 2 gates?
            # Or is it the number of instructions?
            # Standard definition: total number of gates.
            if instr.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instr.targets_copy()) // 2
            else:
                count += len(instr.targets_copy())
    return count

def check():
    circuit = stim.Circuit.from_file("baseline.stim")
    
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
            
    print(f"Baseline preserves {preserved}/{len(stabilizers)} stabilizers.")
    
    cx = count_cx(circuit)
    vol = calculate_volume(circuit)
    print(f"Baseline metrics: cx_count={cx}, volume={vol}")

if __name__ == "__main__":
    check()
