import stim
import sys
from collections import defaultdict

def get_stabilizers():
    stabs = []
    with open('stabilizers.txt', 'r') as f:
        for line in f:
            if line.strip():
                stabs.append(stim.PauliString(line.strip()))
    return stabs

def analyze_and_solve():
    c_in = stim.Circuit.from_file('input.stim')
    stabs = get_stabilizers()
    
    num_qubits = max(c_in.num_qubits, 100)
    max_q = 0
    for s in stabs:
        max_q = max(max_q, len(s))
    num_qubits = max(num_qubits, max_q)
    
    ops = []
    for instr in c_in:
        if instr.name in ['CX', 'SWAP', 'CZ', 'CY']:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append((instr.name, [targets[k].value, targets[k+1].value]))
        elif instr.name in ['H', 'S', 'X', 'Y', 'Z', 'I', 'RX', 'RY', 'RZ']:
            targets = instr.targets_copy()
            for t in targets:
                ops.append((instr.name, [t.value]))
    
    N = len(ops)
    print(f"Analyzing {N} ops...")
    
    t_suffix = stim.Tableau(num_qubits)
    dangerous_errors = [] 
    
    for i in range(N-1, -1, -1):
        name, targs = ops[i]
        for q in targs:
            for p in ['X', 'Y', 'Z']:
                res = None
                if p == 'X': res = t_suffix.x_output(q)
                elif p == 'Y': res = t_suffix.y_output(q)
                elif p == 'Z': res = t_suffix.z_output(q)
                
                if res.weight > 3:
                     dangerous_errors.append(res)
        
        mini = stim.Circuit()
        mini.append('I', [num_qubits-1])
        mini.append(name, targs)
        t_op = stim.Tableau.from_circuit(mini)
        t_suffix = t_op.then(t_suffix)

    print(f"Found {len(dangerous_errors)} dangerous faults.")
    
    unique_errors_set = set()
    unique_errors_list = []
    for e in dangerous_errors:
        s_e = str(e)
        if s_e not in unique_errors_set:
            unique_errors_set.add(s_e)
            unique_errors_list.append(e)
    unique_errors = unique_errors_list
    print(f"Unique dangerous errors: {len(unique_errors)}")

    stabs_w4 = [ (i, s) for i, s in enumerate(stabs) if s.weight <= 4 ]
    stabs_high = [ (i, s) for i, s in enumerate(stabs) if s.weight > 4 ]
    print(f"Stabilizers: {len(stabs_w4)} low-weight, {len(stabs_high)} high-weight.")
    
    candidates_all = stabs_w4 + stabs_high
    
    detectable_errors = []
    logical_errors = []
    
    for E in unique_errors:
        covered = False
        for i, s in candidates_all:
             if not E.commutes(s):
                 covered = True
                 break
        if covered:
            detectable_errors.append(E)
        else:
            logical_errors.append(E)
            
    print(f"Detectable: {len(detectable_errors)}, Logical/Undetectable: {len(logical_errors)}")
    
    remaining = set(range(len(detectable_errors)))
    chosen_stabs = []
    
    # Pass 1: Low weight
    candidates = stabs_w4
    while remaining:
        best_stab_idx = -1
        best_covered_set = set()
        
        for s_idx, s in candidates:
            if s_idx in [x[0] for x in chosen_stabs]:
                continue
            
            covered_now = set()
            for err_idx in remaining:
                E = detectable_errors[err_idx]
                if not E.commutes(s):
                    covered_now.add(err_idx)
            
            if len(covered_now) > len(best_covered_set):
                best_covered_set = covered_now
                best_stab_idx = s_idx
        
        if best_stab_idx == -1:
            print("Warning: Could not cover all with low-weight.")
            break
            
        chosen_stabs.append((best_stab_idx, stabs[best_stab_idx]))
        remaining -= best_covered_set
        print(f"Selected stab {best_stab_idx} (weight {stabs[best_stab_idx].weight}), remaining: {len(remaining)}")

    # Pass 2: High weight
    if remaining:
        print("Using high weight...")
        candidates = stabs_high
        while remaining:
            best_stab_idx = -1
            best_covered_set = set()
            
            for s_idx, s in candidates:
                if s_idx in [x[0] for x in chosen_stabs]:
                    continue
                
                covered_now = set()
                for err_idx in remaining:
                    E = detectable_errors[err_idx]
                    if not E.commutes(s):
                        covered_now.add(err_idx)
                
                if len(covered_now) > len(best_covered_set):
                    best_covered_set = covered_now
                    best_stab_idx = s_idx
            
            if best_stab_idx == -1:
                print("Error: Could not cover remaining!")
                break
                
            chosen_stabs.append((best_stab_idx, stabs[best_stab_idx]))
            remaining -= best_covered_set
            print(f"Selected stab {best_stab_idx} (weight {stabs[best_stab_idx].weight}), remaining: {len(remaining)}")
            
    print(f"Total stabs: {len(chosen_stabs)}")
    
    c_out = c_in.copy()
    next_ancilla = num_qubits
    final_ancillas = []
    
    for s_idx, s in chosen_stabs:
        anc = next_ancilla
        next_ancilla += 1
        final_ancillas.append(anc)
        
        c_out.append('R', [anc]) 
        c_out.append('H', [anc])
        
        indices = [k for k in range(len(s)) if s[k] != 0]
        for q in indices:
            p = s[q]
            if p == 1: c_out.append('CX', [anc, q])
            elif p == 2: c_out.append('CY', [anc, q])
            elif p == 3: c_out.append('CZ', [anc, q])
        c_out.append('H', [anc])
        c_out.append('M', [anc])
        
    return c_out, final_ancillas

if __name__ == '__main__':
    c_final, ancillas = analyze_and_solve()
    with open('solution.stim', 'w') as f:
        f.write(str(c_final))
    with open('ancillas.txt', 'w') as f:
        f.write(str(ancillas))
    print("Solution generated.")
