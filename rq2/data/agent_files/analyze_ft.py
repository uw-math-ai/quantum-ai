import stim
import collections
import sys

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def count_faults(circuit, threshold=7):
    ops = []
    for instr in circuit:
        if instr.name in ['CX', 'SWAP', 'CZ', 'CY']:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append((instr.name, [targets[k].value, targets[k+1].value]))
        elif instr.name in ['H', 'S', 'X', 'Y', 'Z', 'I']:
            targets = instr.targets_copy()
            for t in targets:
                ops.append((instr.name, [t.value]))
    return ops

def analyze_faults_brute_force(circuit_file, threshold=7):
    c = load_circuit(circuit_file)
    num_qubits = c.num_qubits
    num_qubits = max(num_qubits, 133)
    
    ops = []
    for instr in c:
        if instr.name in ['CX', 'SWAP', 'CZ', 'CY']:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append((instr.name, [targets[k].value, targets[k+1].value]))
        elif instr.name in ['H', 'S', 'X', 'Y', 'Z', 'I']:
            targets = instr.targets_copy()
            for t in targets:
                ops.append((instr.name, [t.value]))
                
    N = len(ops)
    print(f'Analyzing {N} operations with {num_qubits} qubits...')
    
    stabilizers = []
    with open('stabilizers.txt', 'r') as f:
        for line in f:
            if line.strip():
                stabilizers.append(stim.PauliString(line.strip()))
    print(f'Loaded {len(stabilizers)} stabilizers.')
    
    stab_tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    inv_stab_tableau = stab_tableau.inverse()
    
    def is_stabilizer(p):
        # Check if p is Identity on ancillas (indices >= 133)
        # And check if p[0:133] is in stabilizer group
        
        # Check ancilla part
        if len(p) > 133:
            # We can slice? No.
            # We can check string representation?
            # Or iterate.
            # Stim 1.12+ supports slicing.
            # But simpler: construct p_data and p_ancilla
            pass
            
        # Simpler: just pad the tableau to match p size?
        # But tableau inverse is on 133.
        # Let's slice p.
        p_data = stim.PauliString(133)
        for k in range(133):
             # Copy Pauli
             # x, z = p.get_x(k), p.get_z(k) # Stim < 1.13?
             # Stim 1.15.
             # p[k] returns int?
             # We can use slicing `p[:133]`.
             pass
             
        p_slice = p[:133]
        
        # Check if any ancilla has non-identity
        # p[133:]
        if len(p) > 133:
            p_anc = p[133:]
            if p_anc.weight > 0:
                return False # Error on ancilla is not a data stabilizer
        
        p_mapped = inv_stab_tableau(p_slice)
        s = str(p_mapped)
        return 'X' not in s and 'Y' not in s

    print('Computing error weights using backward Tableau propagation...')
    
    t_suffix = stim.Tableau(num_qubits)
    
    dangerous_ops = collections.defaultdict(list)
    undetectable_dangerous = []
    
    for i in range(N-1, -1, -1):
        name, targs = ops[i]
        
        for q in targs:
            for p_char in ['X', 'Y', 'Z']:
                res = None
                if p_char == 'X':
                    res = t_suffix.x_output(q)
                elif p_char == 'Y':
                    res = t_suffix.y_output(q)
                elif p_char == 'Z':
                    res = t_suffix.z_output(q)
                    
                w = res.weight
                
                if w > threshold: # Strictly greater than threshold (7)
                    # The prompt says 'propagates to less than ...' i.e. <= 7 is OK.
                    # So w > 7 is BAD.
                    
                    if is_stabilizer(res):
                        continue

                    commutes_all = True
                    for stab in stabilizers:
                        if stim.PauliString.commutes(res, stab) == False:
                            commutes_all = False
                            break
                    
                    dangerous_ops[i].append((q, p_char, w, commutes_all))
                    if commutes_all:
                         undetectable_dangerous.append((i, q, p_char, w))

        full_mini = stim.Circuit()
        full_mini.append('I', [num_qubits-1]) 
        full_mini.append(name, targs)
        t_op_full = stim.Tableau.from_circuit(full_mini)
        t_suffix = t_op_full.then(t_suffix)
        
        if i % 100 == 0:
            print(f'Step {i}')
            
    return dangerous_ops, undetectable_dangerous

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'candidate.stim'
    
    dangers, undetectables = analyze_faults_brute_force(filename, 7)
    print(f'Found dangerous faults at {len(dangers)} locations.')
    print(f'Found {len(undetectables)} undetectable high-weight faults (Logical Errors).')
    
    if undetectables:
        print('Example undetectable faults:')
        for u in undetectables[:5]:
            print(u)
        x_count = sum(1 for _, _, p, _ in undetectables if p == 'X')
        y_count = sum(1 for _, _, p, _ in undetectables if p == 'Y')
        z_count = sum(1 for _, _, p, _ in undetectables if p == 'Z')
        print(f'Undetectable counts: X={x_count}, Y={y_count}, Z={z_count}')
    else:
        print('All dangerous faults are detectable by stabilizers!')
