import stim
import sys

def analyze(circuit_path):
    with open(circuit_path, 'r') as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    
    # We force 49 qubits (0-48). If circuit uses more, we expand.
    num_qubits = 49
    # Pre-scan for max qubit
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                num_qubits = max(num_qubits, t.value + 1)
    
    print(f"Num qubits: {num_qubits}")
    
    # Flatten ops
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

    print(f"Total ops: {len(ops)}")
    
    data_indices = set(range(49))
    flag_indices = set(range(49, num_qubits))
    
    THRESHOLD = 4
    
    # Backward propagation
    t_rem = stim.Tableau(num_qubits)
    
    bad_faults = []
    
    for k in range(len(ops)-1, -1, -1):
        name, targs = ops[k]
        
        # Check faults injected AFTER op k
        for q in targs:
            for p_type in [1, 3]: # X, Z
                ps = stim.PauliString(num_qubits)
                ps[q] = p_type 
                
                final_ps = t_rem(ps)
                
                w_data = 0
                is_flagged = False
                
                for i in range(num_qubits):
                    p = final_ps[i] # 0=I, 1=X, 2=Y, 3=Z
                    if p != 0:
                        if i in data_indices:
                            w_data += 1
                        elif i in flag_indices:
                            # Flagging means X error on flag qubit
                            if p == 1:
                                is_flagged = True
                
                if w_data >= THRESHOLD and not is_flagged:
                    bad_faults.append({
                        'loc': k,
                        'op_name': name,
                        'op_targs': targs,
                        'qubit': q,
                        'type': 'X' if p_type == 1 else 'Z',
                        'weight': w_data
                    })
        
        # Update T_rem
        mini_c = stim.Circuit()
        # Force size
        mini_c.append("I", [num_qubits-1])
        mini_c.append(name, targs)
        t_op = stim.Tableau.from_circuit(mini_c)
        t_rem = t_op.then(t_rem)

    print(f"Found {len(bad_faults)} bad faults.")
    
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
    if len(sys.argv) > 1:
        analyze(sys.argv[1])
    else:
        analyze("data/gemini-3-pro-preview/agent_files_ft/original.stim")
