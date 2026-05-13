import stim

def transform_circuit():
    with open("circuit_input.stim", "r") as f:
        circuit_str = f.read()
    
    circuit = stim.Circuit(circuit_str)
    
    # Flatten instructions
    flat_ops = []
    for instr in circuit:
        if instr.name == "CX":
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                flat_ops.append(stim.CircuitInstruction("CX", [targets[k], targets[k+1]]))
        elif instr.name in ["H", "S", "X", "Y", "Z", "I", "R", "MX", "MY", "MZ"]:
            for t in instr.targets_copy():
                flat_ops.append(stim.CircuitInstruction(instr.name, [t]))
        else:
            # Keep other instructions as is (TICK, etc)
            flat_ops.append(instr)
            
    # Find chains
    # chains[q] = {'start': idx, 'end': idx, 'count': n}
    # We need to store completed chains.
    completed_chains = []
    current_chains = {} # q -> chain_info
    
    for i, op in enumerate(flat_ops):
        # Determine which qubits are 'touched'
        targets = op.targets_copy()
        touched = [t.value for t in targets if t.is_qubit_target]
        
        # Check if this op extends a chain or breaks it
        is_cx_control = False
        control_q = -1
        if op.name == "CX":
            control_q = touched[0]
            target_q = touched[1]
            is_cx_control = True
            
        # Update chains
        # For the control qubit of a CX, we extend the chain.
        # For ALL other touched qubits, we break their chains.
        
        # Careful: CX 0 1. 0 is control. 1 is target.
        # 0's control-chain extends.
        # 1's control-chain breaks (because 1 is acted upon).
        
        # Handle control_q
        if is_cx_control:
            if control_q in current_chains:
                current_chains[control_q]['end'] = i
                current_chains[control_q]['count'] += 1
            else:
                current_chains[control_q] = {'start': i, 'end': i, 'count': 1}
        else:
            # If op is not CX (e.g. H), it breaks control chain on touched qubits
            if len(touched) > 0:
                pass # Logic handled below in "touched" loop
        
        # Handle breaks
        for q in touched:
            if is_cx_control and q == control_q:
                continue # Already handled extension
            
            # For q, this op is NOT a control-extension. So it breaks q's chain.
            if q in current_chains:
                completed_chains.append((q, current_chains[q]))
                del current_chains[q]
                
    # Finish remaining chains
    for q, chain in current_chains.items():
        completed_chains.append((q, chain))
        
    # Filter chains
    # Threshold 4
    to_flag = [c for c in completed_chains if c[1]['count'] >= 3]
    
    print(f"Found {len(to_flag)} chains to flag.")
    
    # Assign flags and insertions
    # insertions[i] = list of ops (before/after?)
    # Let's say insertions_before[i]
    # insertions_after[i]
    
    insertions_before = {}
    insertions_after = {}
    
    # Find max qubit index to allocate ancillas
    max_q = 0
    for op in flat_ops:
        for t in op.targets_copy():
            if t.is_qubit_target:
                max_q = max(max_q, t.value)
    
    next_ancilla = max_q + 1
    ancillas = []
    
    for q, chain in to_flag:
        flag_q = next_ancilla
        next_ancilla += 1
        ancillas.append(flag_q)
        
        start_i = chain['start']
        end_i = chain['end']
        
        # Insert CX q flag before start
        if start_i not in insertions_before:
            insertions_before[start_i] = []
        insertions_before[start_i].append(stim.CircuitInstruction("CX", [stim.GateTarget(q), stim.GateTarget(flag_q)]))
        
        # Insert CX q flag after end
        if end_i not in insertions_after:
            insertions_after[end_i] = []
        insertions_after[end_i].append(stim.CircuitInstruction("CX", [stim.GateTarget(q), stim.GateTarget(flag_q)]))
        
    # Reconstruct circuit
    new_circuit = stim.Circuit()
    for i, op in enumerate(flat_ops):
        if i in insertions_before:
            for ins in insertions_before[i]:
                new_circuit.append(ins)
        new_circuit.append(op)
        if i in insertions_after:
            for ins in insertions_after[i]:
                new_circuit.append(ins)
                
    # Add measurements for ancillas
    # We should also initialize them?
    # Stim assumes |0> by default? No, usually inputs are |0>.
    # But if we want explicit M at the end.
    if ancillas:
        new_circuit.append(stim.CircuitInstruction("M", [stim.GateTarget(a) for a in ancillas]))
        
    # Save
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))
        
    with open("ancillas.txt", "w") as f:
        f.write(",".join(str(a) for a in ancillas))
        
    print(f"Generated candidate with {len(ancillas)} flags.")

if __name__ == "__main__":
    transform_circuit()
