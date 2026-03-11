import stim
import itertools

def get_single_qubit_cliffords():
    # BFS to find shortest sequence for all 24 single qubit cliffords
    gates = ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "C_XYZ", "C_ZYX"]
    
    # Map tableau string to shortest sequence
    found = {}
    
    # Depth 0
    t0 = stim.Tableau(1) # Identity
    found[str(t0)] = []
    
    queue = [([], t0)]
    
    # We need 24 unique tableaus
    # Actually checking string representation is enough for uniqueness of Cliffords?
    # Stim tableau string is canonical? Yes.
    
    while len(found) < 24 and queue:
        seq, tab = queue.pop(0)
        
        if len(seq) >= 3: # Limit depth just in case
             continue
             
        for g in gates:
            new_seq = seq + [g]
            
            # Apply gate
            new_tab = tab.copy()
            if g != "I":
                gate_c = stim.Circuit()
                gate_c.append(g, [0])
                gate_tab = stim.Tableau.from_circuit(gate_c)
                new_tab.append(gate_tab, [0])
                
            s = str(new_tab)
            if s not in found:
                found[s] = new_seq
                queue.append((new_seq, new_tab))
                
            if len(found) >= 24:
                break
                
    return found

def optimize_tail():
    # Load candidate
    with open("candidate.stim", "r") as f:
        circuit = stim.Circuit(f.read())
        
    # Split into head and tail
    head = stim.Circuit()
    tail = stim.Circuit()
    cz_idx = -1
    for i, instr in enumerate(circuit):
        if instr.name == "CZ":
            cz_idx = i
            
    for i in range(cz_idx + 1):
        head.append(circuit[i])
    for i in range(cz_idx + 1, len(circuit)):
        tail.append(circuit[i])
        
    # Precompute optimal sequences
    print("Generating Clifford table...")
    lookup = get_single_qubit_cliffords()
    print(f"Found {len(lookup)} Cliffords.")
    
    # Process tail
    num_qubits = 45
    new_tail_gates = [[] for _ in range(num_qubits)]
    
    # Accumulate tableau for each qubit
    qubit_tableaus = [stim.Tableau(1) for _ in range(num_qubits)]
    
    for instr in tail:
        if instr.name == "TICK":
            continue
        for t in instr.targets_copy():
            q = t.value
            # Update tableau
            # instr.name acts on q
            # We treat q as 0
            gate_c = stim.Circuit()
            gate_c.append(instr.name, [0])
            gate_tab = stim.Tableau.from_circuit(gate_c)
            qubit_tableaus[q].append(gate_tab, [0])
            
    # Find optimal sequence for each
    new_tail_circ = stim.Circuit()
    
    # We want to group by gate type to keep circuit compact/layered if possible
    # But for volume it doesn't matter.
    # We'll just append qubit by qubit or layer by layer.
    # Layering is better for depth.
    # To minimize depth, we should try to parallelize.
    # But first just get the gates.
    
    optimized_ops = []
    for q in range(num_qubits):
        tab = qubit_tableaus[q]
        s = str(tab)
        if s in lookup:
            ops = lookup[s]
            # remove I
            ops = [op for op in ops if op != "I"]
            optimized_ops.append((q, ops))
        else:
            print(f"Warning: Clifford for qubit {q} not found in table!")
            # This shouldn't happen if we covered all 24.
            # Fallback?
            pass
            
    # Naive reconstruction: append all gates
    for q, ops in optimized_ops:
        for op in ops:
            new_tail_circ.append(op, [q])
            
    final_circuit = head + new_tail_circ
    
    with open("candidate_optimized_v2.stim", "w") as f:
        f.write(str(final_circuit))

if __name__ == "__main__":
    optimize_tail()
