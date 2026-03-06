import stim

def optimize_circuit(circuit):
    # Convert to list of instructions
    instructions = list(circuit)
    
    # We want to cancel adjacent H gates on the same qubit.
    # We can track the state of "pending H" on each qubit.
    # But gates can be parallel.
    # Simplest approach: iterate and build new circuit, keeping track of "pending H" for each qubit.
    
    new_instructions = []
    pending_h = set() # qubits that have a pending H
    
    for inst in instructions:
        if inst.name == "H":
            targets = inst.targets_copy()
            for t in targets:
                if t in pending_h:
                    pending_h.remove(t) # Cancel H-H
                else:
                    pending_h.add(t)
        else:
            # Flush pending H on qubits involved in this instruction
            # BUT we need to be careful. H commutes with some gates? No, H generally doesn't commute.
            # So if an instruction touches a qubit with pending H, we must emit the H first.
            
            targets = set(inst.targets_copy())
            # For 2-qubit gates, targets are pairs.
            # But stim instructions store targets as a flat list.
            
            # Identify which qubits in pending_h are touched by this instruction
            touched = [q for q in pending_h if q in targets]
            
            # Emit H for touched qubits
            if touched:
                new_instructions.append(stim.CircuitInstruction("H", touched))
                for q in touched:
                    pending_h.remove(q)
            
            # Emit the instruction itself
            new_instructions.append(inst)
            
    # Flush remaining pending H
    if pending_h:
        new_instructions.append(stim.CircuitInstruction("H", list(pending_h)))
        
    return stim.Circuit().from_args(steps=False, args=new_instructions) # Use instructions directly? No.
    # Simpler: append to a new circuit
    
    final_circuit = stim.Circuit()
    for inst in new_instructions:
        final_circuit.append(inst)
    return final_circuit

# Load candidate
with open("candidate_graph.stim", "r") as f:
    circuit = stim.Circuit(f.read())

optimized = optimize_circuit(circuit)

# Count metrics
def count_metrics(circ):
    cx_count = 0
    volume = 0
    for inst in circ:
        if inst.name == "CX":
            n = len(inst.targets_copy()) // 2
            cx_count += n
            volume += n
        elif inst.name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "XCZ", "YCX"]:
             volume += len(inst.targets_copy())
    return cx_count, volume

cx, vol = count_metrics(optimized)
print(f"Optimized Metrics: CX={cx}, Volume={vol}")

with open("candidate_optimized.stim", "w") as f:
    f.write(str(optimized))
