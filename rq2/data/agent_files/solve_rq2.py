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
    
    # 1. Identify Dangerous Faults
    # A fault is (instruction_index, target_index, type)
    # We simulate the circuit and track error propagation.
    
    num_qubits = max(c_in.num_qubits, 100)
    # Check max qubit in stabs
    max_q = 0
    for s in stabs:
        max_q = max(max_q, len(s))
    num_qubits = max(num_qubits, max_q)
    
    # Build operations list for easier indexing
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
        # Ignore others for now
    
    N = len(ops)
    print(f"Analyzing {N} ops...")
    
    t_suffix = stim.Tableau(num_qubits)
    
    dangerous_errors = [] # List of PauliStrings (error on data)
    
    # Backward pass to find error weights
    for i in range(N-1, -1, -1):
        name, targs = ops[i]
        
        # Simulate faults at this location
        # Faults: X, Y, Z on each target
        for q in targs:
            for p in ['X', 'Y', 'Z']:
                # Get the propagated error at the end
                res = None
                if p == 'X': res = t_suffix.x_output(q)
                elif p == 'Y': res = t_suffix.y_output(q)
                elif p == 'Z': res = t_suffix.z_output(q)
                
                # Check weight on data qubits (0..80)
                # We assume data qubits are those touched by the circuit/stabilizers
                # Stabs are length 81. So 0..80.
                w = 0
                error_on_data = stim.PauliString(num_qubits)
                
                # Manual weight count on first 81 qubits
                # Also construct the PauliString for checking commutativity
                # Stim's weight is total weight.
                # If circuit uses ancillas, we should ignore them?
                # The input circuit uses 0..80. No ancillas yet.
                # So res.weight is accurate.
                
                if res.weight > 3:
                     dangerous_errors.append(res)
        
        # Update tableau
        mini = stim.Circuit()
        mini.append('I', [num_qubits-1])
        mini.append(name, targs)
        t_op = stim.Tableau.from_circuit(mini)
        t_suffix = t_op.then(t_suffix)

    print(f"Found {len(dangerous_errors)} dangerous faults.")
    
    # 2. Select Stabilizers to Measure
    selected_indices = set()
    
    undetected = 0
    
    # Optimize: Greedy coverage
    # dangerous_errors is a list of PauliStrings.
    # We want to pick stabs such that for every error E in dangerous_errors,
    # there is at least one S in selected stabs s.t. commute(E, S) == False.
    
    # To optimize, we can check which errors are already covered.
    
    uncovered_errors = []
    for E in dangerous_errors:
        uncovered_errors.append(E)
        
    print(f"Covering {len(uncovered_errors)} errors...")
    
    # Simple Greedy:
    # 1. Check which are already covered by chosen stabs (initially none)
    # 2. Pick a stab that covers the most remaining errors.
    # But checking commutativity is fast.
    
    # Optimization: Filter stabs by weight. Prefer weight <= 4.
    stabs_w4 = [ (i, s) for i, s in enumerate(stabs) if s.weight <= 4 ]
    stabs_high = [ (i, s) for i, s in enumerate(stabs) if s.weight > 4 ]
    print(f"Stabilizers: {len(stabs_w4)} low-weight, {len(stabs_high)} high-weight.")

    # Prioritize low weight.
    # First pass: Try to cover with ONLY low weight (<=4)
    # If remaining > 0, then use high weight.
    
    candidates = stabs_w4
    
    # ... logic for loop ...
    
    chosen_stabs = []
    
    # Loop for low weight
    while remaining:
        best_stab_idx = -1
        best_covered_set = set()
        
        for s_idx, s in candidates:
            if s_idx in [x[0] for x in chosen_stabs]:
                continue
            
            # Check how many remaining it covers
            covered_now = set()
            for err_idx in remaining:
                E = detectable_errors[err_idx]
                if not E.commutes(s):
                    covered_now.add(err_idx)
            
            if len(covered_now) > len(best_covered_set):
                best_covered_set = covered_now
                best_stab_idx = s_idx
        
        if best_stab_idx == -1:
            print("Warning: Could not cover all errors with low-weight stabilizers.")
            break
            
        chosen_stabs.append((best_stab_idx, stabs[best_stab_idx]))
        remaining -= best_covered_set
        print(f"Selected stab {best_stab_idx} (weight {stabs[best_stab_idx].weight}), remaining errors: {len(remaining)}")

    # Second pass: High weight if needed
    if remaining:
        print("Attempting to cover remaining with high-weight stabilizers...")
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
                print("Error: Could not cover remaining errors even with high-weight!")
                break
                
            chosen_stabs.append((best_stab_idx, stabs[best_stab_idx]))
            remaining -= best_covered_set
            print(f"Selected stab {best_stab_idx} (weight {stabs[best_stab_idx].weight}), remaining errors: {len(remaining)}")

    
    # 3. Generate Output Circuit
    c_out = c_in.copy()
    
    # Append measurements
    # Use ancillas starting from max(num_qubits used in stabs or circuit) + 1
    # num_qubits calculation earlier:
    # num_qubits = max(num_qubits, max_q)
    # This max_q was length of stabs.
    # So num_qubits is sufficient.
    
    next_ancilla = num_qubits
    
    for s_idx, s in chosen_stabs:
        anc = next_ancilla
        next_ancilla += 1
        
        # Init
        c_out.append('R', [anc]) 
        
        c_out.append('H', [anc])
        
        indices = [k for k in range(len(s)) if s[k] != 0]
        for q in indices:
            p = s[q]
            if p == 1: # X
                c_out.append('CX', [anc, q])
            elif p == 2: # Y
                c_out.append('CY', [anc, q])
            elif p == 3: # Z
                c_out.append('CZ', [anc, q])
        c_out.append('H', [anc])
        c_out.append('M', [anc])
        
    return c_out, [q for q in range(81, next_ancilla)]

if __name__ == '__main__':
    c_final, ancillas = analyze_and_solve()
    
    # Output to stdout for capture (or file)
    # The tool expects me to call return_result.
    # I will write the result to a file "solution.stim" and "ancillas.txt"
    # So I can read them and call return_result.
    
    with open('solution.stim', 'w') as f:
        f.write(str(c_final))
        
    with open('ancillas.txt', 'w') as f:
        f.write(str(ancillas))
    
    print("Solution generated.")
