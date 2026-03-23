import stim
import sys
from collections import Counter

def analyze(circuit_path, stabs_path):
    with open(circuit_path, 'r') as f:
        circuit_text = f.read()
    
    with open(stabs_path, 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
        # Remove commas if present
        stabs = [s.replace(',', '') for s in stabs]

    circuit = stim.Circuit(circuit_text)
    
    # 153 data qubits (0 to 152)
    DATA_QUBITS = set(range(153))
    
    num_qubits = 153
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                num_qubits = max(num_qubits, t.value + 1)
    
    FLAG_QUBITS = set(range(153, num_qubits))
    print(f"Data qubits: {len(DATA_QUBITS)}")
    print(f"Flag qubits: {len(FLAG_QUBITS)} ({sorted(list(FLAG_QUBITS))})")
    
    ops = []
    for instr in circuit.flattened():
        name = instr.name
        targets = instr.targets_copy()
        if name in ["CX", "SWAP", "CZ", "ISWAP", "CNOT"]:
             for k in range(0, len(targets), 2):
                 t1 = targets[k].value
                 t2 = targets[k+1].value
                 ops.append((name, [t1, t2]))
        elif name in ["H", "S", "X", "Y", "Z", "I", "R", "RX", "RY", "RZ"]:
             for t in targets:
                 ops.append((name, [t.value]))
        else:
             pass 
             
    THRESHOLD = 7 # floor((15-1)/2)
    
    # Reference tableau for stabilizers
    try:
        ps_stabs = [stim.PauliString(s) for s in stabs]
        ref_tableau = stim.Tableau.from_stabilizers(ps_stabs, allow_redundant=True, allow_underconstrained=True)
        ref_inv = ref_tableau.inverse()
        print("Stabilizer tableau built successfully.")
    except Exception as e:
        print(f"Error building reference tableau: {e}")
        ref_inv = None

    t_rem = stim.Tableau(num_qubits)
    bad_faults = []

    print(f"Analyzing {len(ops)} operations...")
    
    for k in range(len(ops)-1, -1, -1):
        name, targs = ops[k]
        
        for q in targs:
            for p_type in [1, 3]: # X, Z (Y is X*Z)
                ps = stim.PauliString(num_qubits)
                ps[q] = p_type 
                final_ps = t_rem(ps)
                
                # Check for stabilizer
                is_stab = False
                if ref_inv:
                    data_only = True
                    for i in range(num_qubits):
                         if i >= 153 and final_ps[i] != 0:
                             data_only = False
                             break
                    
                    if data_only:
                        d_ps = stim.PauliString(153)
                        for i in range(153):
                             d_ps[i] = final_ps[i]
                        
                        mapped = ref_inv(d_ps)
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
                        if i in DATA_QUBITS:
                            w_data += 1
                        elif i in FLAG_QUBITS:
                            # Flag triggers on X error (measured as -1)
                            # Stim 1=X, 2=Y, 3=Z
                            # Measurement in Z basis: X and Y flip it.
                            if p == 1 or p == 2:
                                is_flagged = True
                
                if w_data > THRESHOLD and not is_flagged:
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

    print(f"Found {len(bad_faults)} bad faults.")
    
    loc_counts = {}
    for f in bad_faults:
        loc = f['loc']
        if loc not in loc_counts:
            loc_counts[loc] = 0
        loc_counts[loc] += 1
        
    sorted_locs = sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("Top bad locations:")
    for loc, count in sorted_locs[:20]:
        op_name, op_targs = ops[loc]
        print(f"Loc {loc}: {op_name} {op_targs} -> {count} bad faults")
        ex = next(f for f in bad_faults if f['loc'] == loc)
        print(f"  Ex: Q{ex['qubit']} {ex['type']} -> W={ex['weight']}")

if __name__ == "__main__":
    circuit_file = "candidate_rq2.stim"
    if len(sys.argv) > 1:
        circuit_file = sys.argv[1]
    
    analyze(circuit_file, "current_stabs.txt")
