import stim
import collections

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def get_stabilizer_paulis(stabilizers, num_qubits):
    paulis = []
    for s_str in stabilizers:
        p = stim.PauliString(s_str)
        # Pad if necessary? No, string length implies size.
        # But we need consistent size.
        if len(p) < num_qubits:
             # This assumes identity elsewhere? Or s_str should be full length.
             # The input file has 105 chars.
             pass
        paulis.append(p)
    return paulis

def commutates(p1, p2):
    return stim.PauliString(p1).commutes(stim.PauliString(p2))

def optimize():
    circuit_path = "C:/Users/anpaz/Repos/quantum-ai/rq2/circuit_input.stim"
    stabs_path = "C:/Users/anpaz/Repos/quantum-ai/rq2/stabilizers_input.txt"
    
    print("Loading inputs...")
    base_circuit = load_circuit(circuit_path)
    stabilizer_strs = parse_stabilizers(stabs_path)
    
    # Determine num_qubits
    ops = list(base_circuit.flattened())
    max_q = 0
    for op in ops:
        for t in op.targets_copy():
            if t.is_qubit_target:
                max_q = max(max_q, t.value)
    
    # Data qubits are 0..104 based on stabilizer file length.
    num_data = 105
    num_qubits = max(num_data, max_q + 1)
    
    stabilizers = []
    for s in stabilizer_strs:
        # Extend to num_qubits (padding with I)
        p = stim.PauliString(s)
        # Manually pad or resize?
        # stim.PauliString doesn't resize easily.
        # But checks against it will work if we slice.
        stabilizers.append(p)
        
    current_circuit = base_circuit.copy()
    flags = []
    
    # Iterate to add flags
    for iteration in range(10): # Try up to 10 flags
        print(f"Iteration {iteration}")
        
        # Analyze current circuit
        # We need to simulate faults.
        
        # Re-calc num_qubits as we add ancillas
        ops = list(current_circuit.flattened())
        max_q_curr = 0
        for op in ops:
            for t in op.targets_copy():
                if t.is_qubit_target:
                    max_q_curr = max(max_q_curr, t.value)
        
        sim_qubits = max(num_qubits, max_q_curr + 1)
        
        # Build T_future backward
        t_future = stim.Tableau(sim_qubits) # Identity
        
        bad_faults = [] # List of (propagated_error_pauli)
        
        print(f"  Analyzing {len(ops)} ops...")
        for i in range(len(ops) - 1, -1, -1):
            op = ops[i]
            
            # Faults after op
            targets = []
            for t_ptr in op.targets_copy():
                if t_ptr.is_qubit_target:
                    targets.append(t_ptr.value)
            
            # Check faults
            for q in targets:
                # We care about faults on ANY qubit active?
                # Usually just targets.
                
                for p_char in ['X', 'Y', 'Z']:
                    p = stim.PauliString(sim_qubits)
                    if p_char == 'X': p[q] = 1
                    elif p_char == 'Y': p[q] = 2
                    elif p_char == 'Z': p[q] = 3
                    
                    prop = t_future(p)
                    
                    # Check weight on data qubits
                    w = 0
                    for k in range(num_data):
                        if prop[k]: w += 1
                        
                    if w >= 4:
                        # Check flags
                        flagged = False
                        for f_idx in flags:
                            # Trigger if X (1) or Y (2) on flag?
                            # "Flagging means X error on flag qubit".
                            # Pauli X is 1. Y is 2. Z is 3.
                            # If we measure Z, X flips it. Y flips it. Z does not.
                            # So 1 or 2.
                            if prop[f_idx] in [1, 2]:
                                flagged = True
                                break
                        
                        if not flagged:
                            bad_faults.append(prop)
                            
            # Update T_future
            op_c = stim.Circuit()
            op_c.append("I", [sim_qubits-1])
            op_c.append(op)
            op_t = stim.Tableau.from_circuit(op_c)
            t_future = op_t.then(t_future)
            
        print(f"  Bad faults: {len(bad_faults)}")
        
        if len(bad_faults) == 0:
            print("  Success! No bad faults.")
            break
            
        # Select best stabilizer to measure
        # We want S such that {S, E} = 0 for most E in bad_faults.
        
        best_stab_idx = -1
        best_score = -1
        
        # Heuristic: verify only top 100 bad faults to save time?
        # Or all.
        sample_faults = bad_faults
        if len(sample_faults) > 1000:
             sample_faults = sample_faults[:1000]
             
        scores = []
        for s_idx, stab in enumerate(stabilizers):
            score = 0
            for err in sample_faults:
                # Commutation check.
                # stab is length 105. err is larger.
                # slice err to 105.
                # But err might have terms on ancillas?
                # Stabilizers only define on data.
                # So just check commutation on data part.
                # If err commutes with S on data part, it commutes (assuming S is I elsewhere).
                
                # Manual commutation check
                # X and Z anti-commute.
                # sum of (x1*z2 + z1*x2) % 2.
                anti = 0
                for k in range(num_data):
                    # p1: stab[k]. p2: err[k]
                    # 0=I, 1=X, 2=Y, 3=Z
                    # X(1) Z(3) -> 1*1 + 0*1 = 1 (anti)
                    # X(1) Y(2) -> Y=XZ. X(XZ) = Z. (XZ)X = -Z. Anti.
                    # Z(3) Y(2) -> Z(XZ) = X. (XZ)Z = -X. Anti.
                    # Formula: is_anti = (x1 && z2) != (x2 && z1)
                    # Decompose:
                    # 1(X): x=1, z=0
                    # 2(Y): x=1, z=1
                    # 3(Z): x=0, z=1
                    
                    s_code = stab[k]
                    e_code = err[k]
                    
                    sx = (s_code == 1 or s_code == 2)
                    sz = (s_code == 2 or s_code == 3)
                    
                    ex = (e_code == 1 or e_code == 2)
                    ez = (e_code == 2 or e_code == 3)
                    
                    if (sx and ez) != (ex and sz):
                        anti += 1
                
                if (anti % 2) == 1:
                    score += 1
            
            scores.append(score)
            if score > best_score:
                best_score = score
                best_stab_idx = s_idx
                
        print(f"  Best stabilizer {best_stab_idx} catches {best_score}/{len(sample_faults)} faults.")
        
        if best_score == 0:
            print("  No stabilizer helps! Stuck.")
            break
            
        # Add flagged gadget for best_stab_idx
        # We need 2 ancillas: Measure (M) and Flag (F)
        # Determine current max qubit used to find new indices
        ops = list(current_circuit.flattened())
        max_q_curr = 0
        for op in ops:
            for t in op.targets_copy():
                if t.is_qubit_target:
                    max_q_curr = max(max_q_curr, t.value)
        
        # New ancillas
        anc_m = max_q_curr + 1
        anc_f = max_q_curr + 2
        
        # Ensure distinct from num_qubits base range (0..104)
        if anc_m < 105: anc_m = 105
        if anc_f <= anc_m: anc_f = anc_m + 1
        
        print(f"  Adding flagged gadget on M={anc_m}, F={anc_f} for stabilizer {best_stab_idx}")
        
        gadget = stim.Circuit()
        gadget.append("H", [anc_m])
        # F initialized in 0. No H on F needed if we use CX A F to detect X on A.
        # But wait, we measure F in Z basis.
        # If A has X error, CX A F flips F to 1 (X_A -> X_A X_F).
        # So X_F is 1.
        # So no H on F.
        
        stab = stabilizers[best_stab_idx]
        stab_ops = []
        for k in range(num_data):
            code = stab[k]
            if code == 1: stab_ops.append(("CX", k))
            elif code == 2: stab_ops.append(("CY", k))
            elif code == 3: stab_ops.append(("CZ", k))
            
        # Split ops
        mid = len(stab_ops) // 2
        
        # First half
        for i in range(mid):
            gate, target = stab_ops[i]
            gadget.append(gate, [anc_m, target])
            
        # Flag interaction
        gadget.append("CX", [anc_m, anc_f])
        
        # Second half
        for i in range(mid, len(stab_ops)):
            gate, target = stab_ops[i]
            gadget.append(gate, [anc_m, target])
            
        gadget.append("H", [anc_m])
        
        current_circuit += gadget
        flags.append(anc_f)
        flags.append(anc_m)
        
    # Save result
    with open("solution.stim", "w") as f:
        f.write(str(current_circuit))
    print("Saved solution.stim")

if __name__ == "__main__":
    optimize()
