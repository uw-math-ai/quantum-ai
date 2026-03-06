import stim
import sys

def get_cx_count(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    for s_str in stabilizers:
        p = stim.PauliString(s_str)
        if sim.peek_observable_expectation(p) == 1:
            preserved += 1
    return preserved

try:
    with open('my_task_baseline.stim', 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    with open('my_task_stabilizers.txt', 'r') as f:
        stabilizers = [l.strip() for l in f.readlines() if l.strip()]

    print(f"Checking {len(stabilizers)} stabilizers on {circuit.num_qubits} qubits.")
    
    preserved = check_stabilizers(circuit, stabilizers)
    print(f"Preserved: {preserved}/{len(stabilizers)}")
    
    cx_count = get_cx_count(circuit)
    print(f"CX count: {cx_count}")
    
    # Calculate volume (total gates)
    volume = sum(len(op.targets_copy()) for op in circuit) 
    # Wait, volume usually means total gate count? Or total operations? 
    # "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
    # Usually we count 1 for single qubit, 1 for two qubit? Or number of operations?
    # Usually: sum over instructions of len(targets) / (1 or 2).
    # But Stim instructions can have multiple targets. 
    # E.g. H 0 1 2 is 3 H gates.
    
    vol = 0
    for op in circuit:
        if op.name in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
            continue
        # For simplicity, count total targets applied
        vol += len(op.targets_copy())
        if op.name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP", "CY"]:
             # These take 2 targets per gate, so len/2 gates. 
             # But the prompt says "total gate count". If H 0 1 2 is 3 gates, then len(targets) is correct.
             # If CX 0 1 2 3 is 2 CX gates, then len(targets) is 4. So len(targets) is NOT gate count.
             # CX 0 1 is 1 gate. Targets=2.
             pass
             
    # Recalculate volume more carefully
    real_volume = 0
    for op in circuit:
        if op.name in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
            continue
        n_args = 1
        if op.name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP", "CY", "XCZ", "XCY", "XCX"]:
            n_args = 2
        
        args = len(op.targets_copy())
        real_volume += args // n_args

    print(f"Volume: {real_volume}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
