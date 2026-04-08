import stim
import sys

def verify_candidate():
    with open("candidate.stim", "r") as f:
        circuit_str = f.read()
    
    circuit = stim.Circuit(circuit_str)
    
    with open("ancillas.txt", "r") as f:
        ancillas_str = f.read()
        flag_qubits = set([int(x) for x in ancillas_str.split(",") if x])
        
    data_qubits = set(range(174)) # 0..173
    
    # Flatten ops
    flat_ops = []
    for instr in circuit:
        if instr.name in ["H", "CX", "S", "X", "Y", "Z", "I", "M"]:
            targets = instr.targets_copy()
            if instr.name == "CX":
                for k in range(0, len(targets), 2):
                    flat_ops.append((instr.name, [targets[k].value, targets[k+1].value]))
            elif instr.name == "M":
                # M targets
                for t in targets:
                    flat_ops.append((instr.name, [t.value]))
            else:
                for t in targets:
                    flat_ops.append((instr.name, [t.value]))
                    
    # Find max qubit
    max_q = 0
    for name, targets in flat_ops:
        max_q = max(max_q, max(targets))
    total_qubits = max_q + 1
    
    print(f"Verifying circuit with {len(flat_ops)} ops, {total_qubits} qubits.")
    
    # We use tableau simulation backwards
    t = stim.Tableau(total_qubits)
    
    # For flags:
    # If we measure a flag, we want to know if it is flipped.
    # A fault P causes a flip if P propagates to X on the measured qubit (for Z measurement).
    # Since we measure in Z, X error flips the result.
    # The Tableau tracks X and Z propagation.
    # If we are at the end, T is identity.
    # A Z-measurement on q checks Z observable.
    # A fault P triggers q if P anticommutes with Z_q?
    # No, we simulate the error propagation.
    # P_final is the error on the state before measurement.
    # Measurement M_q checks Z_q.
    # If P_final has X_q or Y_q, it flips the measurement.
    # So we check if `t.x_output(q)` or `t.y_output(q)` ?
    # Wait, `t` maps input Pauli to output Pauli.
    # If fault is P at location i.
    # P_final = T(P).
    # If P_final on flag_q is X or Y, then flag is triggered (flipped).
    # Note: If P_final is I or Z, flag is not triggered.
    
    severe_faults = 0
    
    for i in range(len(flat_ops)-1, -1, -1):
        name, targets = flat_ops[i]
        
        # Check faults at this location
        involved = targets
        
        for q in involved:
            for p_type in ["X", "Z"]:
                res_pauli = t.x_output(q) if p_type == "X" else t.z_output(q)
                
                # Check data weight
                w = 0
                for dq in range(174):
                    p = res_pauli[dq]
                    if p != 0:
                        w += 1
                
                if w >= 4:
                    # Check flags
                    triggered = False
                    for fq in flag_qubits:
                        # Check if Pauli on fq is X or Y
                        # 1=X, 2=Y, 3=Z
                        p_f = res_pauli[fq]
                        if p_f == 1 or p_f == 2:
                            triggered = True
                            break
                    
                    if not triggered:
                        severe_faults += 1
                        # print(f"Fault at {i} on {q} type {p_type} weight {w} NOT DETECTED")
        
        # Update Tableau
        if name == "M":
            # Measurement does not change the unitary propagation of errors?
            # It projects.
            # But for error propagation analysis, we usually treat M as identity or stop?
            # If we measure, we stop propagating?
            # The tableau should represent the circuit.
            # Measurements in Stim are operations.
            # But `stim.Tableau` does not support 'M'.
            # However, M is usually at the end.
            # If we iterate backwards, we start at M.
            # M doesn't change the Pauli.
            # So we can ignore M for Tableau update?
            # Yes, unless we feed forward.
            # Here we just measure at the end.
            pass
        else:
            t.prepend(stim.Tableau.from_named_gate(name), targets)
            
    print(f"Verification complete. Remaining severe faults: {severe_faults}")

if __name__ == "__main__":
    verify_candidate()
