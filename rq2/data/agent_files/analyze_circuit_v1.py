import stim
from typing import List, Tuple, Set

def get_stabilizers() -> List[stim.PauliString]:
    stabs = [
        "XXXXIII", "XIXIXIX", "IIXXXXI", 
        "ZZZZIII", "ZIZIZIZ", "IIZZZZI"
    ]
    # Length 7
    return [stim.PauliString(s) for s in stabs]

def get_all_stabilizers_group(generators: List[stim.PauliString]) -> List[stim.PauliString]:
    current_group = [stim.PauliString("I"*7)]
    
    for gen in generators:
        new_elements = []
        for existing in current_group:
            prod = existing * gen
            # Check if prod is already in current_group or new_elements
            # Check just the Pauli string part? No, full equality
            is_new = True
            for x in current_group:
                if x == prod:
                    is_new = False
                    break
            if is_new:
                for x in new_elements:
                    if x == prod:
                        is_new = False
                        break
            
            if is_new:
                new_elements.append(prod)
        current_group.extend(new_elements)
        
    return current_group

def get_error_weight(error: stim.PauliString, stabilizer_group: List[stim.PauliString]) -> int:
    min_w = 999
    # Only consider data qubits 0-6
    # If there are ancilla qubits (7+), we ignore them for "data qubit error weight".
    # The error string might be longer if we added ancillas.
    
    # Slice error to first 7 qubits
    # We can do this by just checking indices 0-6
    
    for s in stabilizer_group:
        # s is length 7. error might be longer.
        # Construct combined P on 0-6
        # We need to manually combine because lengths differ
        w = 0
        for k in range(7):
            p1 = error[k]
            p2 = s[k]
            # Multiplication table: I=0, X=1, Z=2, Y=3
            # 1*1=0, 2*2=0, 3*3=0
            # 1*2=3, 2*1=3
            # 1*3=2, 3*1=2
            # 2*3=1, 3*2=1
            # 0*x=x
            
            # Stim logic:
            # stim.PauliString doesn't support element-wise mul easily if lengths differ
            # But we can just check if p1 != p2? No.
            # We want weight of (error * s).
            # (E * S)[k] != I
            
            # Using stim's multiplication:
            # Create a full length S padded with I
            full_s = stim.PauliString(len(error))
            for i in range(7):
                if s[i] == 1: full_s[i] = 1 # X
                elif s[i] == 2: full_s[i] = 2 # Z
                elif s[i] == 3: full_s[i] = 3 # Y
            
            combined = error * full_s
            
            # Count weight on 0-6
            cur_w = 0
            for i in range(7):
                if combined[i] != 0:
                    cur_w += 1
            w = cur_w
            
        if w < min_w:
            min_w = w
    return min_w

def analyze_circuit(circuit_str: str):
    circuit = stim.Circuit(circuit_str)
    print(f"Analyzing circuit with {circuit.num_qubits} qubits...")
    
    # 1. Verify stabilizers
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    generators = get_stabilizers()
    for g in generators:
        # Extend generator to circuit size if needed
        g_ext = stim.PauliString(circuit.num_qubits)
        for i in range(7):
            if g[i] == 1: g_ext[i] = 1
            elif g[i] == 2: g_ext[i] = 2
            elif g[i] == 3: g_ext[i] = 3
            
        if sim.peek_observable_expectation(g_ext) != 1:
            print(f"STABILIZER FAIL: {g} not preserved")
            return

    print("Stabilizers preserved.")
    
    # 2. Fault Tolerance
    # Use ACTUAL stabilizers of the circuit (including state stabilizers)
    # This captures logical state stabilizers like Z_L if prepared.
    actual_stabilizers = sim.canonical_stabilizers()
    stabilizer_group = get_all_stabilizers_group(actual_stabilizers)
    
    # Flatten circuit
    flat_ops = []
    for op in circuit:
        targets = op.targets_copy()
        if op.name in ["CX", "SWAP", "CZ"]:
            for k in range(0, len(targets), 2):
                flat_ops.append((op.name, targets[k:k+2]))
        elif op.name in ["M", "R", "MR"]:
             # Measurements/Resets are operations too
             for t in targets:
                 flat_ops.append((op.name, [t]))
        else:
            for t in targets:
                flat_ops.append((op.name, [t]))
                
    faults_T = [] # List of (op_idx, type, qubit, weight, flagged) where weight > 1
    
    total_faults = 0
    
    # Simulate every fault
    for i, (name, targets) in enumerate(flat_ops):
        # Determine qubits involved
        qubits = [t.value for t in targets if t.is_qubit_target]
        
        # Determine possible faults
        # "single-qubit Pauli fault can occur"
        # Where? On the qubits involved in the gate.
        # After the gate.
        
        for q in qubits:
            for p_type in ["X", "Y", "Z"]:
                total_faults += 1
                
                # Check if flagged
                # Propagate P through remainder
                
                # Remainder circuit
                rem_circuit = stim.Circuit()
                for j in range(i + 1, len(flat_ops)):
                    op_n, op_t = flat_ops[j]
                    t_vals = [t.value for t in op_t]
                    rem_circuit.append(op_n, t_vals)
                    
                # Propagate
                p = stim.PauliString(circuit.num_qubits)
                if p_type == "X": p[q] = 1
                elif p_type == "Z": p[q] = 2
                elif p_type == "Y": p[q] = 3
                
                flagged = False
                
                # Manual propagation to handle measurements
                current_p = p
                
                for op in rem_circuit:
                    if op.name in ["M", "MR", "R"]: # Measurement or Reset
                        # Reset clears error on that qubit (if Z error? X error?)
                        # Reset X -> prepares |0>.
                        # If error was X, it flips the prepared state? No.
                        # R is usually "Measure Z, if 1 then X".
                        # For simplicity, treat R as "M then Init".
                        # If M checks P and anticommutes -> Flag.
                        # If P on q is X/Y and we measure Z -> Anticommutes -> Flag.
                        # If P on q is Z and we measure Z -> Commutes -> No Flag.
                        # Then P on q becomes I (collapsed).
                        
                        # Check commutation
                        # M targets
                        for t in op.targets_copy():
                            q_idx = t.value
                            # If we measure Z (standard M)
                            # Check if P has X or Y on q_idx
                            p_val = current_p[q_idx]
                            if p_val == 1 or p_val == 3: # X or Y
                                flagged = True
                            
                            # After measurement/reset, the error on q_idx is cleared (or becomes Z?)
                            # If it's a destructive measurement, the qubit is gone/reset.
                            # If we flag, we stop.
                            if flagged: break
                            
                            # If not flagged, P must match measurement basis (Z or I).
                            # If R, error is cleared.
                            if op.name in ["R", "MR"]:
                                current_p[q_idx] = 0
                    
                    if flagged: break
                    
                    # If unitary, propagate
                    if op.name not in ["M", "MR", "R"]:
                        # Single gate circuit
                        gate_c = stim.Circuit()
                        # Force correct number of qubits by adding identity on last qubit
                        # if the gate doesn't touch it, or even if it does (I is safe)
                        gate_c.append("I", [circuit.num_qubits - 1])
                        gate_c.append(op)
                        current_p = stim.Tableau.from_circuit(gate_c)(current_p)
                
                if not flagged:
                    # Calculate weight
                    w = get_error_weight(current_p, stabilizer_group)
                    if w > 1:
                        faults_T.append({
                            "op_idx": i,
                            "op": f"{name} {qubits}",
                            "fault": f"{p_type} on {q}",
                            "weight": w,
                            "flagged": False
                        })
                else:
                    # It was flagged. We still need to know if it was in T (weight > 1).
                    # But if it's flagged, it contributes 0 to the penalty sum.
                    # Wait, the score denominator is |T|.
                    # T is set of faults with E > t.
                    # Does E > t refer to the *unflagged* error?
                    # Or the error that *would have occurred*?
                    # "Let E(C', C) be the number of errors in C' compared with C after propagation."
                    # "T(S(C)) := { C' in S(C) | E(C', C) > t }"
                    # This definition does not mention flags.
                    # So T includes ALL faults that cause >1 error, regardless of flagging.
                    
                    # So we MUST calculate weight even if flagged?
                    # "pi(C')=1" (flagged -> pi=0? No. "If no flag fires... pi=1". So Flagged -> pi=0).
                    # Term: 1[pi(C')=1 AND E > t]
                    # If Flagged (pi=0), the term is 0.
                    # If Not Flagged (pi=1), term is 1 (if E > t).
                    # So we sum unflagged high-weight errors.
                    # Divided by |T| (total high-weight errors).
                    
                    # So yes, we need to know if this flagged fault is in T.
                    # To do that, we need its weight *as if* it wasn't flagged?
                    # Or is the weight defined on the final state?
                    # If flagged, we correct it? No, "triggers a flag ancilla".
                    # Usually "fault tolerant" means we discard if flagged.
                    # So the error on data is irrelevant if flagged.
                    # But to compute the score as defined, we need |T|.
                    # If E(C', C) is defined on the final state, and we flagged,
                    # does the final state count as having error?
                    # The definition of E is "number of errors ... after propagation".
                    # It likely refers to the Pauli error on the data qubits.
                    # If we flagged, the Pauli error is still there (unless we corrected).
                    # But the prompt implies we just discard.
                    # Let's assume T includes flagged errors too.
                    # So we must calculate weight even if flagged.
                    
                    # Propagate to end ignoring measurements (except for commutation check which we already did)
                    # We just propagate through unitaries.
                    # (Assuming measurements don't back-propagate to change data qubits? They don't).
                    # (Assuming measurements don't change the Pauli error on *other* qubits? They don't).
                    # So we can just propagate P through all unitaries.
                    
                    # Re-propagate full circuit for weight calculation
                    p_w = stim.PauliString(circuit.num_qubits)
                    if p_type == "X": p_w[q] = 1
                    elif p_type == "Z": p_w[q] = 2
                    elif p_type == "Y": p_w[q] = 3
                    
                    for j in range(i + 1, len(flat_ops)):
                        op_n, op_t = flat_ops[j]
                        if op_n not in ["M", "MR", "R"]:
                             t_vals = [t.value for t in op_t]
                             gate_c = stim.Circuit()
                             gate_c.append("I", [circuit.num_qubits - 1])
                             gate_c.append(op_n, t_vals)
                             p_w = stim.Tableau.from_circuit(gate_c)(p_w)
                             
                    w = get_error_weight(p_w, stabilizer_group)
                    
                    if w > 1:
                        faults_T.append({
                            "op_idx": i,
                            "op": f"{name} {qubits}",
                            "fault": f"{p_type} on {q}",
                            "weight": w,
                            "flagged": True
                        })

    # Calculate Score
    # T = faults_T
    len_T = len(faults_T)
    bad_T = [f for f in faults_T if not f['flagged']]
    len_bad = len(bad_T)
    
    if len_T > 0:
        score = 1.0 - (len_bad / len_T)
    else:
        score = 1.0
        
    print(f"Total Faults: {total_faults}")
    print(f"Size of T (weight > 1): {len_T}")
    print(f"Unflagged in T: {len_bad}")
    print(f"Score: {score}")
    
    # Print top 5 bad faults
    print("Top 5 Unflagged High-Weight Faults:")
    for f in bad_T[:5]:
        print(f"  {f['op']} -> {f['fault']} (w={f['weight']})")

if __name__ == "__main__":
    circuit_text = """
    CX 1 0 0 1 1 0
    H 0 2
    CX 0 2 0 3 0 4 0 6
    H 1
    CX 1 0 1 2 1 4 2 3 2 4 2 5 3 5 4 5 6 4 6 5
    """
    analyze_circuit(circuit_text)
