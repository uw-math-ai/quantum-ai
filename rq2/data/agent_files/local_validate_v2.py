
import stim
import sys

def get_stabilizers():
    return [
        "IIIIXIIIIIXIIIXIXIXIIIIIXIIIIIIIIIIII", "IIIIIXIIIIIIXIIXIIIXIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIXIIXXIIIIIIIIIXIIIII", "IIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIXX", "IIIXIIIIIIIIIIIIIIIIIIXXIIXIIXIIIIIIX", "XIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIXXIII", "IIIIIIIIIXIIIIIXIIIXIIIIIIIIXIIIIIIII", "XIIIIIIIIIIIIIIIXIIIIIIIXIXIIXIIXIIII", "IXXIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIII", "IXXIIIIXXIIXIIIIIIIIIIIIIIIIIIIIIIXII", "IIIIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXII", "IIIIIIIIIIXIIIIIIXXIIXIIIIIIIIIIIIIII", "XIIXIXXIIIIIXIIIIIIIIIIIIIIIIXIIIIIII", "IIXIIIIIIIIXIXIIIIIIIIIIIIIIIIXIIIIII", "IIIIIIIXIIIXIXIIIIIIIIXXIXIIIIIIIIIII", "IIIIIIIXXIIIIIXIXIIIIIIXIIXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIXIIXIIXIIIIIIXXXIII", "IIIXIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXX", "IIIIZIIIIIZIIIZIZIZIIIIIZIIIIIIIIIIII", "IIIIIZIIIIIIZIIZIIIZIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZIIZZIIIIIIIIIZIIIII", "IIIIIIIIIIIIIIIIIIIIIIZIIZIIIIIIIIIZZ", "IIIZIIIIIIIIIIIIIIIIIIZZIIZIIZIIIIIIZ", "ZIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIZZIII", "IIIIIIIIIZIIIIIZIIIZIIIIIIIIZIIIIIIII", "ZIIIIIIIIIIIIIIIZIIIIIIIZIZIIZIIZIIII", "IZZIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIIII", "IZZIIIIZZIIZIIIIIIIIIIIIIIIIIIIIIIZII", "IIIIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZII", "IIIIIIIIIIZIIIIIIZZIIZIIIIIIIIIIIIIII", "ZIIZIZZIIIIIZIIIIIIIIIIIIIIIIZIIIIIII", "IIZIIIIIIIIZIZIIIIIIIIIIIIIIIIZIIIIII", "IIIIIIIZIIIZIZIIIIIIIIZZIZIIIIIIIIIII", "IIIIIIIZZIIIIIZIZIIIIIIZIIZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIZIIZIIZIIIIIIZZZIII", "IIIZIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZZ"
    ]

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    for s_str in stabilizers:
        # Check expectation
        # We need to construct a PauliString
        pauli = stim.PauliString(s_str)
        if sim.peek_observable_expectation(pauli) == 1:
            preserved += 1
    return preserved, len(stabilizers)

def analyze_faults(circuit, data_qubits, flag_qubits):
    ops = list(circuit.flattened())
    
    # Determine max qubit index
    max_q = 0
    for op in ops:
        for t in op.targets_copy():
            if t.is_qubit_target:
                max_q = max(max_q, t.value)
    num_qubits = max_q + 1
    
    # Propagator tableau
    prop = stim.Tableau(num_qubits)
    
    bad_faults = []
    threshold = 3
    
    # Iterate backwards
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        targets = op.targets_copy()
        
        # Analyze errors (after op[i])
        active_qubits = []
        for t in targets:
            if t.is_qubit_target:
                active_qubits.append(t.value)
        
        for q in active_qubits:
            # We check X, Z. Y is X*Z.
            # Get X output and Z output
            px = prop.x_output(q)
            pz = prop.z_output(q)
            
            for p_type in ['X', 'Z', 'Y']:
                if p_type == 'X':
                    p_final = px
                elif p_type == 'Z':
                    p_final = pz
                else: # Y
                    p_final = px * pz 
                
                # Check data weight
                w = 0
                triggered = False
                
                # Iterate indices 0 to num_qubits-1
                # To be fast, we can use string or just loop
                # Stim PauliString length is num_qubits
                
                # Check data qubits
                for dq in data_qubits:
                    if dq < len(p_final):
                        # 0=I, 1=X, 2=Y, 3=Z
                        if p_final[dq] != 0:
                            w += 1
                
                # Check flag qubits
                for fq in flag_qubits:
                    if fq < len(p_final):
                        # Flag if X error (1)
                        # What if Y error (2)? Y = iXZ. Contains X.
                        # Usually Y counts as flagging too if measuring Z basis?
                        # Let's assume ANY non-Z error on flag triggers (X or Y).
                        # Wait, Z error on flag measured in Z basis does nothing.
                        # X or Y flips the bit.
                        # So op_val == 1 or op_val == 2.
                        op_val = p_final[fq]
                        if op_val == 1 or op_val == 2:
                            triggered = True
                            break
                
                if w > threshold and not triggered:
                    bad_faults.append( (i, q, p_type, w) )

        # Update prop
        prop.prepend_operation(op.name, targets)
        
    return bad_faults

if __name__ == "__main__":
    import sys
    # Read entire input
    circuit_str = sys.stdin.read()
    circuit = stim.Circuit(circuit_str)
    
    data_qubits = list(range(37))
    flag_qubits = []
    
    max_q = 0
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                max_q = max(max_q, t.value)
    
    if max_q > 36:
        flag_qubits = list(range(37, max_q + 1))
        
    stabilizers = get_stabilizers()
    p, t = check_stabilizers(circuit, stabilizers)
    print(f"Stabilizers: {p}/{t}")
    
    faults = analyze_faults(circuit, data_qubits, flag_qubits)
    print(f"Bad faults: {len(faults)}")
    if faults:
        print(f"First 5 bad faults: {faults[:5]}")
