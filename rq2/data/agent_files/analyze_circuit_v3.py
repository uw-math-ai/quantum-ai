import stim
import sys

def analyze(circuit_path):
    with open(circuit_path, 'r') as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    
    num_qubits = 49
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                num_qubits = max(num_qubits, t.value + 1)
    
    ops = []
    for instr in circuit.flattened():
        name = instr.name
        targets = instr.targets_copy()
        if name in ["CX", "SWAP", "CZ", "ISWAP"]:
             for k in range(0, len(targets), 2):
                 t1 = targets[k].value
                 t2 = targets[k+1].value
                 ops.append((name, [t1, t2]))
        elif name in ["H", "S", "X", "Y", "Z", "I"]:
             for t in targets:
                 ops.append((name, [t.value]))
        else:
             pass 

    data_indices = set(range(49))
    flag_indices = set(range(49, num_qubits))
    THRESHOLD = 4
    
    # Check stabilizers
    # We build a tableau from the stabilizers.
    # The stabilizers define a codespace.
    # Any operator P is equivalent to P' if P * P' is in S.
    # But for error propagation: E is the error.
    # If E is in S, it acts trivially on code states.
    # So effective error is Identity. Weight 0.
    
    # We construct a Tableau that maps Z basis states to the stabilizer states.
    # T(Z_i) = S_i.
    # Then T^-1 maps S_i to Z_i.
    # If P is in S, T^-1(P) is in span(Z).
    # i.e., T^-1(P) consists only of I and Z.
    
    stabs = [
"XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI", "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX", "IIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXX", "ZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZI", "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ", "IIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZ", "XXXIIIIXXXIIIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIIIIIIII", "XXXIIIIIIIIIIIXXXIIIIIIIIIIIXXXIIIIIIIIIIIXXXIIII", "IIIIIIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIXXXIIIIXXXIIII", "ZZZIIIIZZZIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIIIIIIII", "ZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIII", "IIIIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIZZZIIIIZZZIIII"
    ]
    
    ref_tableau = None
    try:
        ps_stabs = [stim.PauliString(s) for s in stabs]
        # Tableau.from_stabilizers creates a tableau whose stabilizers include the input list.
        # It requires the input list to be valid and commuting.
        ref_tableau = stim.Tableau.from_stabilizers(ps_stabs, allow_redundant=True, allow_underconstrained=True)
        ref_inv = ref_tableau.inverse()
    except Exception as e:
        print(f"Error building reference tableau: {e}")
        ref_inv = None

    t_rem = stim.Tableau(num_qubits)
    bad_faults = []

    for k in range(len(ops)-1, -1, -1):
        name, targs = ops[k]
        
        for q in targs:
            for p_type in [1, 3]: # X, Z
                ps = stim.PauliString(num_qubits)
                ps[q] = p_type 
                final_ps = t_rem(ps)
                
                # Check for stabilizer
                is_stab = False
                if ref_inv:
                    # Check if error is on data only
                    # Actually, if error involves ancilla, it CANNOT be a code stabilizer.
                    # Unless ancilla is in + state and error is X?
                    # The code stabilizers are defined on data qubits (0-48).
                    # Any error with support outside 0-48 is not a code stabilizer.
                    
                    data_only = True
                    for i in range(num_qubits):
                         if i >= 49 and final_ps[i] != 0:
                             data_only = False
                             break
                    
                    if data_only:
                        # Project to 49
                        d_ps = stim.PauliString(49)
                        for i in range(49):
                             d_ps[i] = final_ps[i]
                        
                        mapped = ref_inv(d_ps)
                        # Check if Z/I only
                        is_z = True
                        for i in range(len(mapped)):
                            if mapped[i] == 1 or mapped[i] == 2:
                                is_z = False
                                break
                        if is_z:
                            is_stab = True
                
                if is_stab:
                    continue
                
                w_data = 0
                is_flagged = False
                for i in range(num_qubits):
                    p = final_ps[i]
                    if p != 0:
                        if i in data_indices:
                            w_data += 1
                        elif i in flag_indices:
                            if p == 1:
                                is_flagged = True
                
                if w_data >= THRESHOLD and not is_flagged:
                    bad_faults.append({
                        'loc': k,
                        'op': f"{name} {targs}",
                        'qubit': q,
                        'type': 'X' if p_type==1 else 'Z',
                        'weight': w_data
                    })
        
        # Update T_rem
        mini_c = stim.Circuit()
        if num_qubits > 0: mini_c.append("I", [num_qubits-1])
        mini_c.append(name, targs)
        t_rem = stim.Tableau.from_circuit(mini_c).then(t_rem)

    print(f"Found {len(bad_faults)} bad faults (excluding stabilizers).")
    
    loc_counts = {}
    for f in bad_faults:
        loc = f['loc']
        if loc not in loc_counts:
            loc_counts[loc] = 0
        loc_counts[loc] += 1
        
    sorted_locs = sorted(loc_counts.items(), key=lambda x: x[0])
    
    print("Top bad locations:")
    for loc, count in sorted_locs[:20]:
        op_name, op_targs = ops[loc]
        print(f"Loc {loc}: {op_name} {op_targs} -> {count} bad faults")
        ex = next(f for f in bad_faults if f['loc'] == loc)
        print(f"  Ex: Q{ex['qubit']} {ex['type']} -> W={ex['weight']}")

if __name__ == "__main__":
    analyze(sys.argv[1] if len(sys.argv)>1 else "candidate_initial.stim")
