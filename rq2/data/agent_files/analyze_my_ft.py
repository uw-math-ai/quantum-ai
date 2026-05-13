import stim
import sys

def load_stabilizers(filename):
    stabilizers = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith('+'):
                line = line[1:]
            # Replace _ with I
            line = line.replace('_', 'I')
            stabilizers.append(stim.PauliString(line))
    return stabilizers

def analyze_faults():
    circuit = stim.Circuit.from_file("current.stim")
    stabilizers = load_stabilizers("all_stabilizers.txt")
    
    num_qubits = circuit.num_qubits
    # Determine data qubits from stabilizer length
    stab_len = len(stabilizers[0])
    if stab_len > num_qubits:
        num_qubits = stab_len
    
    # We'll assume stabilizers cover data qubits 0 to stab_len-1
    data_qubits = range(stab_len)
    
    print(f"Num qubits: {num_qubits}, Num stabilizers: {len(stabilizers)}")

    primitive_ops = []
    for op in circuit.flattened():
        name = op.name
        targets = op.targets_copy()
        arity = 1
        if name in ['CX', 'CZ', 'SWAP', 'ISWAP', 'CNOT', 'CY', 'ZC', 'XC', 'YC']:
            arity = 2
        elif name in ['H', 'S', 'X', 'Y', 'Z', 'I', 'RX', 'RY', 'RZ']:
            arity = 1
        
        for i in range(0, len(targets), arity):
            chunk = targets[i:i+arity]
            primitive_ops.append((name, chunk))
            
    num_primitive = len(primitive_ops)
    print(f"Ops: {num_primitive}")
    
    bad_faults = []
    
    # Pre-compute stabilizer Pauli strings for fast access
    # We can use Stim's tableau method to handle multiplication?
    # Actually PauliString supports multiplication.
    
    # To optimize, we can just do the check for specific ops or random sample first?
    # No, we need all. 1200 is small.
    
    # Current best circuit is what we have.
    
    for k in range(num_primitive):
        name, targets = primitive_ops[k]
        
        suffix = stim.Circuit()
        suffix.append("I", [num_qubits - 1])
        for s_name, s_targets in primitive_ops[k+1:]:
            suffix.append(s_name, s_targets)
            
        t = stim.Tableau.from_circuit(suffix)
        
        for target in targets:
            if not target.is_qubit_target: continue
            q = target.value
            
            for p_type in ['X', 'Z']: # Check X and Z faults (Y is X*Z)
                if p_type == 'X':
                    out_pauli = t.x_output(q)
                else:
                    out_pauli = t.z_output(q)
                
                # Check weight on data qubits
                # Convert to stim.PauliString?
                # Tableau.output returns PauliString.
                
                # Reduction
                reduced_pauli = out_pauli.copy()
                
                # Greedy reduction
                changed = True
                while changed:
                    changed = False
                    current_wt = 0
                    # Calculate weight on data qubits
                    for i in data_qubits:
                        if reduced_pauli[i] != 0: # 0=I, 1=X, 2=Y, 3=Z
                            current_wt += 1
                            
                    for stab in stabilizers:
                        # Try multiplying
                        cand = reduced_pauli * stab
                        # Calculate weight
                        cand_wt = 0
                        for i in data_qubits:
                            if cand[i] != 0:
                                cand_wt += 1
                        
                        if cand_wt < current_wt:
                            reduced_pauli = cand
                            current_wt = cand_wt
                            changed = True
                            # Restart loop to be greedy
                            break 
                
                if current_wt >= 4: # Condition: < 4
                    bad_faults.append(f"Op {k} {name} on {q} type {p_type} -> wt {current_wt}")
                    
    print(f"Bad faults: {len(bad_faults)}")
    if len(bad_faults) > 0:
        print("First 10 bad faults:")
        for b in bad_faults[:10]:
            print(b)
            
if __name__ == "__main__":
    analyze_faults()
