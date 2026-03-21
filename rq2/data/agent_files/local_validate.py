
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
        pauli = stim.PauliString(s_str)
        if sim.peek_observable_expectation(pauli) == 1:
            preserved += 1
    return preserved, len(stabilizers)

def analyze_faults(circuit, data_qubits, flag_qubits):
    num_qubits = circuit.num_qubits
    # Determine max index actually used
    max_q = 0
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                max_q = max(max_q, t.value)
    
    num_qubits = max_q + 1
    prop = stim.Tableau(num_qubits)
    
    ops = list(circuit.flattened())
    bad_faults = []
    threshold = 3
    
    # Iterate backwards
    for i in range(len(ops) - 1, -1, -1):
        op = ops[i]
        
        # We are analyzing faults AFTER op[i].
        # At this point, `prop` is the Clifford from (i+1) to End.
        # So injecting error P here means final error is prop(P).
        
        # Check errors on active qubits
        targets = op.targets_copy()
        active_qubits = []
        for t in targets:
            if t.is_qubit_target:
                active_qubits.append(t.value)
        
        for q in active_qubits:
            for p_type in ['X', 'Y', 'Z']:
                # Get final Pauli
                if p_type == 'X':
                    p_final = prop.x_output(q)
                elif p_type == 'Z':
                    p_final = prop.z_output(q)
                elif p_type == 'Y':
                    # Y = iXZ
                    px = prop.x_output(q)
                    pz = prop.z_output(q)
                    p_final = px * pz 
                
                # Check weight and flags
                data_weight = 0
                triggered = False
                
                # We need to iterate the PauliString manually or converting to string
                # String conversion is safest for now
                s_final = str(p_final)
                # s_final format: "+_XZ..." or "-_XZ..."
                # First char is sign +/-, then _ (delimiter) ? No.
                # Stim format: "+XZ_Z..." depending on version.
                # Usually: "+IXZ..."
                # Let's use indices.
                # `len(p_final)` is num_qubits
                
                for dq in data_qubits:
                    if dq < len(p_final):
                        # Use getting item?
                        # Trying to access integer value of operator
                        # We can use p_final[dq]
                        op_val = p_final[dq] # 0=I, 1=X, 2=Y, 3=Z
                        if op_val != 0:
                            data_weight += 1
                
                for fq in flag_qubits:
                    if fq < len(p_final):
                        op_val = p_final[fq]
                        # Flag if X error (or Y error, which contains X)
                        # Is Y error measured as -1 in Z basis? No, Y in Z basis is random?
                        # Usually flag qubit is measured in Z basis to detect X errors.
                        # If we assume "Flagging means X error", then X or Y is bad?
                        # Standard flag gadget: CNOT propagates X to Ancilla as X.
                        # So Ancilla has X error.
                        # If Ancilla has Z error, measuring Z doesn't see it.
                        # If Ancilla has Y error, measuring Z sees random?
                        # But typically fault tolerance analysis looks at Pauli errors.
                        # "Flagging means X error on flag qubit."
                        # Let's assume ONLY X counts. (op_val == 1).
                        if op_val == 1:
                            triggered = True
                
                if data_weight > threshold and not triggered:
                    bad_faults.append( (i, q, p_type, data_weight) )

        # Update prop: prepend gate
        # `prepend_operation` applies gate before current tableau
        prop.prepend_operation(op.name, op.targets_copy())
        
    return bad_faults

if __name__ == "__main__":
    circuit_str = sys.stdin.read()
    circuit = stim.Circuit(circuit_str)
    
    data_qubits = list(range(37))
    flag_qubits = []
    
    max_q = circuit.num_qubits - 1
    # Check if we added flags (indices > 36)
    # The circuit might use higher indices if we modified it.
    # For now, hardcode data=0..36
    
    # If the circuit uses qubits > 36, they are flags
    # We find used qubits
    used_qubits = set()
    for op in circuit.flattened():
        for t in op.targets_copy():
            if t.is_qubit_target:
                used_qubits.add(t.value)
    
    for q in used_qubits:
        if q > 36:
            flag_qubits.append(q)
            
    stabilizers = get_stabilizers()
    
    preserved, total = check_stabilizers(circuit, stabilizers)
    print(f"Stabilizers preserved: {preserved}/{total}")
    
    bad_faults = analyze_faults(circuit, data_qubits, flag_qubits)
    print(f"Bad faults count: {len(bad_faults)}")
    
