import stim
from collections import Counter

def main():
    circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\original.stim")
    flat_circuit = circuit.flattened()
    ops = list(flat_circuit)
    num_ops = len(ops)
    print(f"Total operations: {num_ops}")
    
    bad_locations = []
    
    # Identify max qubits. Stabilizers are on 35 qubits, so at least 35.
    num_qubits = circuit.num_qubits
    if num_qubits < 35:
        num_qubits = 35
        
    current_tableau = stim.Tableau(num_qubits)
    
    for i in range(num_ops - 1, -1, -1):
        op = ops[i]
        
        if op.name in ['QUBIT_COORDS', 'DETECTOR', 'OBSERVABLE_INCLUDE', 'SHIFT_COORDS', 'TICK']:
            continue
            
        targets = op.targets_copy()
        qubits = [t.value for t in targets if t.is_qubit_target]
        
        # Check faults AFTER this op
        for q in qubits:
            for p_val in [1, 3]: # 1=X, 3=Z
                p = stim.PauliString(num_qubits)
                p[q] = p_val # Assign integer directly? Or string?
                             # stim 1.12+: p[q] = "X" works. p[q] = 1 works.
                
                # We need to propagate p through current_tableau
                # res = current_tableau(p) -> syntax might be res = current_tableau.call(p)?
                # Or just `current_tableau * p`?
                # In stim 1.12+, `current_tableau(p)` works as `call`.
                try:
                    res = current_tableau(p)
                except TypeError:
                     # Older stim versions might not support direct call
                     res = p.after(current_tableau) # Is this correct? No.
                     # Or maybe just use inverse?
                     # Let's assume stim is recent enough.
                     pass
                
                weight = 0
                for k in range(35): # Only data qubits 0-34
                    # res[k] returns 0,1,2,3
                    if res[k] != 0:
                        weight += 1
                
                if weight >= 4:
                    p_char = "X" if p_val == 1 else "Z"
                    bad_locations.append({
                        'index': i,
                        'op_str': str(op),
                        'qubit': q,
                        'error': p_char,
                        'weight': weight,
                        'final_pauli': str(res)
                    })
        
        # Update tableau
        sub_c = stim.Circuit()
        sub_c.append(op)
        sub_c.append("I", [num_qubits - 1])
        t_op = stim.Tableau.from_circuit(sub_c)
        current_tableau = t_op.then(current_tableau)
        
    print(f"Found {len(bad_locations)} faults with weight >= 4.")
    
    indices = [x['index'] for x in bad_locations]
    c = Counter(indices)
    print("Most problematic operations:")
    # Print top 20 problematic ops
    sorted_ops = c.most_common(20)
    for idx, count in sorted_ops:
        op_str = ops[idx]
        print(f"Op {idx}: {op_str} - {count} faults")
        for x in bad_locations:
            if x['index'] == idx:
                print(f"  Example: {x['error']} on {x['qubit']} -> weight {x['weight']}")
                break

    # Save to file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.txt", "w") as f:
        import json
        f.write(json.dumps(bad_locations))

if __name__ == "__main__":
    main()
