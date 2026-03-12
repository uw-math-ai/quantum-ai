import stim

def optimize_sq(filename_in, filename_out):
    with open(filename_in, 'r') as f:
        c = stim.Circuit(f.read())
        
    last_2q_idx = -1
    for i, instr in enumerate(c):
        # Check for 2-qubit gates. CZ, CX, CY, SWAP, ISWAP, etc.
        # In our case we only expect CZ.
        if instr.name in ["CZ", "CX", "CY", "SWAP", "ISWAP", "ZCZZ", "ZCX", "ZCY"]: 
            last_2q_idx = i
            
    head = c[:last_2q_idx+1]
    tail = c[last_2q_idx+1:]
    
    new_tail = stim.Circuit()
    num_qubits = 37 # Fixed for this task
    
    qubit_ops = {q: stim.Circuit() for q in range(num_qubits)}
    
    for instr in tail:
        # Assuming only single qubit gates in tail
        for t in instr.targets_copy():
            if t.is_qubit_target:
                qubit_ops[t.value].append(instr.name, [0]) # Append to q=0 for simulation
            
    for q in range(num_qubits):
        ops = qubit_ops[q]
        if len(ops) == 0:
            continue
        
        # Simulate on 1 qubit
        t = stim.Tableau.from_circuit(ops)
        
        # Synthesize minimal circuit
        # stim.Tableau.to_circuit() might produce C_XYZ etc.
        synthesized = t.to_circuit()
        
        # Remap to q
        for instr in synthesized:
            new_tail.append(instr.name, [q])
            
    final_c = head + new_tail
    
    with open(filename_out, 'w') as f:
        f.write(str(final_c).replace("tick", ""))

if __name__ == "__main__":
    optimize_sq("candidate_graph_state.stim", "candidate_sq_opt.stim")
