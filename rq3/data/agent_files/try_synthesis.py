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
    # Load stabilizers
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # Try synthesis
    try:
        # We need to pass PauliString objects
        paulis = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        
        # Synthesize circuit
        circuit = tableau.to_circuit(method="elimination")
        
        cx = count_cx(circuit)
        vol = calculate_volume(circuit)
        print(f"Synthesized metrics: cx_count={cx}, volume={vol}")
        
        # Verify preservation
        sim = stim.TableauSimulator()
        sim.do(circuit)
        preserved = 0
        for p in paulis:
            if sim.peek_observable_expectation(p) == 1:
                preserved += 1
        print(f"Synthesized preserves {preserved}/{len(stabilizers)} stabilizers.")
        
        if preserved == len(stabilizers):
            circuit.to_file("candidate_synthesis.stim")
            print("Saved valid synthesis candidate.")
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    check()
