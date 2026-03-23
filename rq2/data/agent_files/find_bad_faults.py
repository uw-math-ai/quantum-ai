import stim
import collections
import sys

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def analyze_faults(circuit_file, threshold=3):
    c = load_circuit(circuit_file)
    num_qubits = c.num_qubits
    num_qubits = max(num_qubits, 135) # Ensure we cover all
    
    ops = []
    # Keep track of original instruction index for better reporting
    op_map = [] 
    
    instr_idx = 0
    for instr in c:
        if instr.name in ['CX', 'SWAP', 'CZ', 'CY']:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append((instr.name, [targets[k].value, targets[k+1].value]))
                op_map.append(instr_idx)
        elif instr.name in ['H', 'S', 'X', 'Y', 'Z', 'I', 'R', 'RX', 'RY', 'RZ']:
            targets = instr.targets_copy()
            for t in targets:
                ops.append((instr.name, [t.value]))
                op_map.append(instr_idx)
        instr_idx += 1
                
    N = len(ops)
    print(f'Analyzing {N} operations with {num_qubits} qubits...')
    
    stabilizers = []
    with open('stabilizers.txt', 'r') as f:
        for line in f:
            if line.strip():
                stabilizers.append(stim.PauliString(line.strip()))
    
    # We need to know which stabilizers are preserved?
    # The prompt implies the final state must be stabilized by these.
    # So if an error commutes with all, it is a logical error (if weight high).
    # But here we only care about weight.
    
    stab_tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    inv_stab_tableau = stab_tableau.inverse()
    
    def is_stabilizer(p):
        # Check if p is in stabilizer group
        # Check ancilla part (if any)
        # Here we assume data qubits are 0..134
        # Stabilizers are defined on 135 qubits?
        # The stabilizers in text are length 135.
        
        if len(p) > 135:
             if p[135:].weight > 0:
                 return False
        
        p_slice = p[:135]
        p_mapped = inv_stab_tableau(p_slice)
        s = str(p_mapped)
        return 'X' not in s and 'Y' not in s

    t_suffix = stim.Tableau(num_qubits)
    
    bad_faults = []
    
    # Backward propagation
    for i in range(N-1, -1, -1):
        name, targs = ops[i]
        
        # Check faults at this location
        # Single qubit faults on each qubit involved
        fault_qubits = targs
        
        for q in fault_qubits:
            for p_char in ['X', 'Z']: # X and Z (Y is X*Z)
                # Check output error
                if p_char == 'X':
                    res = t_suffix.x_output(q)
                elif p_char == 'Z':
                    res = t_suffix.z_output(q)
                    
                # We count weight on DATA qubits.
                # All 0-134 are potentially data qubits?
                # The stabilizers cover 135 qubits.
                # So weight is on 0-134.
                
                # Slicing to get data weight
                w = 0
                # Efficient weight calc?
                # res.weight returns total weight.
                # If we have ancillas (flags), we should exclude them from "data qubits".
                # Flags are usually added later.
                # For now assume all are data.
                w = res.weight
                
                if w > threshold: # > 3
                    if not is_stabilizer(res):
                        # Found a bad fault
                        # Check if it triggers a flag?
                        # Currently no flags.
                        bad_faults.append({
                            'op_idx': i,
                            'original_instr_idx': op_map[i],
                            'gate': name,
                            'targets': targs,
                            'fault_qubit': q,
                            'fault_type': p_char,
                            'weight': w,
                            'error_string': str(res)
                        })

        # Update tableau
        full_mini = stim.Circuit()
        # Add dummy to ensure size
        full_mini.append('I', [num_qubits-1]) 
        full_mini.append(name, targs)
        t_op_full = stim.Tableau.from_circuit(full_mini)
        t_suffix = t_op_full.then(t_suffix)
        
    return bad_faults

if __name__ == '__main__':
    bad = analyze_faults('input.stim', 3)
    print(f"Found {len(bad)} bad faults.")
    if bad:
        print("First 10 bad faults:")
        for b in bad[:10]:
            print(b)
        
        # Write to file
        with open('bad_faults.txt', 'w') as f:
            for b in bad:
                f.write(str(b) + '\n')
