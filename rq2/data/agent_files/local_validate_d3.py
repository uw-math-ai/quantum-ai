import stim
import sys

def get_stabilizers():
    return [
        "IIXIXXX",
        "IXIXIXX",
        "XXXIIXI",
        "IIZIZZZ",
        "IZIZIZZ",
        "ZZZIIZI"
    ]

def check_stabilizers(circuit):
    # Verify stabilizers are preserved/prepared
    # Check if the output state is +1 eigenstate of stabilizers
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    stabs = get_stabilizers()
    preserved = 0
    for s_str in stabs:
        # Convert string to stim.PauliString
        # String has length 7.
        # Maps to qubits 0..6
        # Construct PauliString for num_qubits
        ps = stim.PauliString(circuit.num_qubits)
        for i, char in enumerate(s_str):
            if char == 'X':
                ps[i] = 1 # X
            elif char == 'Y':
                ps[i] = 2 # Y
            elif char == 'Z':
                ps[i] = 3 # Z
        
        if sim.peek_observable_expectation(ps) == 1:
            preserved += 1
            
    return preserved, len(stabs)

def check_fault_tolerance(circuit, data_qubits, flag_qubits):
    # Iterate all single faults
    # Propagate through circuit
    # Check flags and data errors
    
    ops = list(circuit.flattened())
    num_qubits = circuit.num_qubits
    
    # Pre-compute tableaus for operations for speed?
    # Or just use stim.Tableau.from_name per op.
    # Actually, constructing tableaus is fast.
    
    fails = []
    
    # Fault locations: Before the circuit? No, "at each gate location".
    # We can inject fault AFTER each operation.
    # What about before the first op? (Input fault).
    # Usually we assume input |0> is perfect, faults occur in gates.
    # "For each location l in spots(C)... insert P at location l".
    # Usually this means after the gate at l.
    
    # Iterate through ops
    for i in range(len(ops)):
        op = ops[i]
        targets = op.targets_copy()
        
        # Determine active qubits in this op
        active = []
        for t in targets:
            if t.is_qubit_target:
                active.append(t.value)
        
        # For each active qubit, inject X, Y, Z
        for q_fault in active:
            for p_type in ['X', 'Y', 'Z']:
                
                # Propagate this fault to the end
                # Start with this Pauli
                current_pauli = stim.PauliString(num_qubits)
                if p_type == 'X': current_pauli[q_fault] = 1
                if p_type == 'Y': current_pauli[q_fault] = 2
                if p_type == 'Z': current_pauli[q_fault] = 3
                
                flagged = False
                
                # Propagate through REMAINING ops (i+1 to end)
                for j in range(i + 1, len(ops)):
                    next_op = ops[j]
                    
                    if next_op.name == 'M':
                        # Measurement
                        # Check anti-commutation with Z on measured qubits
                        meas_targets = [t.value for t in next_op.targets_copy() if t.is_qubit_target]
                        for mq in meas_targets:
                            # Check if current_pauli has X or Y on mq
                            p_val = current_pauli[mq]
                            if p_val == 1 or p_val == 2: # X or Y
                                # Anti-commutes with Z measurement -> Flips result
                                if mq in flag_qubits:
                                    flagged = True
                            
                            # Measurement collapses Pauli component on mq to I
                            # (Since we know the result, we update our frame? 
                            # Effectively, error on mq is converted to classical error flag, 
                            # and quantum error on mq is removed/randomized).
                            current_pauli[mq] = 0 # I
                            
                    elif next_op.name == 'R':
                        # Reset
                        # Clears errors on targets
                        reset_targets = [t.value for t in next_op.targets_copy() if t.is_qubit_target]
                        for rq in reset_targets:
                            current_pauli[rq] = 0
                            
                    else:
                        # Unitary gate
                        # Conjugate Pauli: P' = U P U^dag
                        # Stim Tableau can do this.
                        # We need a Tableau for the operation.
                        # It's expensive to create Tableau for every op.
                        # Manual rules for common gates.
                        
                        gate = next_op.name
                        gate_targets = [t.value for t in next_op.targets_copy() if t.is_qubit_target]
                        
                        if gate == 'CX':
                            # Process pairs
                            for k in range(0, len(gate_targets), 2):
                                c = gate_targets[k]
                                t = gate_targets[k+1]
                                # CX propagation:
                                # X_c -> X_c X_t
                                # Z_c -> Z_c
                                # X_t -> X_t
                                # Z_t -> Z_c Z_t
                                # Y_c = i X_c Z_c -> i (X_c X_t) Z_c = Y_c X_t
                                # Y_t = i X_t Z_t -> i X_t (Z_c Z_t) = Z_c Y_t
                                
                                # We can implement this by updating the PauliString directly
                                # Get components
                                xc = (current_pauli[c] == 1 or current_pauli[c] == 2)
                                zc = (current_pauli[c] == 3 or current_pauli[c] == 2)
                                xt = (current_pauli[t] == 1 or current_pauli[t] == 2)
                                zt = (current_pauli[t] == 3 or current_pauli[t] == 2)
                                
                                # New components
                                # X_c' = X_c (unchanged?) No.
                                # Check the mapping P -> U P U^dag.
                                # X_c -> X_c X_t.
                                # So if we had X_c, we now have X_c and X_t.
                                # Wait.
                                # If P_in = X_c. P_out = X_c X_t.
                                # If P_in = Z_t. P_out = Z_c Z_t.
                                
                                new_xc = xc
                                new_zc = zc ^ zt
                                new_xt = xt ^ xc
                                new_zt = zt
                                
                                # Reconstruct
                                pc = (1 if new_xc else 0) ^ (3 if new_zc else 0)
                                if new_xc and new_zc: pc = 2 # Y
                                pt = (1 if new_xt else 0) ^ (3 if new_zt else 0)
                                if new_xt and new_zt: pt = 2 # Y
                                
                                current_pauli[c] = pc
                                current_pauli[t] = pt

                        elif gate == 'H':
                            for q in gate_targets:
                                # H: X <-> Z
                                p_val = current_pauli[q]
                                if p_val == 1: current_pauli[q] = 3
                                elif p_val == 3: current_pauli[q] = 1
                                # Y -> -Y (Y stays Y, phase -1 ignored)
                                
                        elif gate == 'S':
                            # S: X -> Y, Z -> Z, Y -> -X
                            for q in gate_targets:
                                p_val = current_pauli[q]
                                if p_val == 1: current_pauli[q] = 2
                                elif p_val == 2: current_pauli[q] = 1
                        
                        elif gate == 'I':
                            pass
                        
                        else:
                            # Fallback to Tableau
                            # Only if needed.
                            # Assuming basic gates for now.
                            # Prompt uses CX, H.
                            pass

                # End of circuit
                # Calculate weight on data qubits
                weight = 0
                for dq in data_qubits:
                    if current_pauli[dq] != 0:
                        weight += 1
                
                # Check condition
                # Fault tolerant if weight < 1 (i.e. 0) OR Flagged
                if weight >= 1 and not flagged:
                    # FAIL
                    fails.append( (i, q_fault, p_type, weight) )

    return fails

if __name__ == "__main__":
    circuit_str = sys.stdin.read()
    circuit = stim.Circuit(circuit_str)
    
    data_qubits = [0, 1, 2, 3, 4, 5, 6]
    flag_qubits = [7, 8, 9, 10, 11, 12]
    
    preserved, total = check_stabilizers(circuit)
    print(f"Stabilizers preserved: {preserved}/{total}")
    
    fails = check_fault_tolerance(circuit, data_qubits, flag_qubits)
    print(f"Bad faults count: {len(fails)}")
    
    # Calculate score
    # FT score = 1 - (1 / |T|) * sum(...)
    # Here, T = fails.
    # If fails is empty, score = 1.
    # If fails is non-empty, score = 1 - (1/|fails|) * |fails| = 0?
    # Wait, the formula: sum over C' of 1[pi=1 AND E>t].
    # My `fails` list contains exactly those cases (pi=1 i.e. not flagged, AND E>t i.e. weight >= 1).
    # So sum = |fails|.
    # Score = 1 - (1/|fails|) * |fails| = 0.
    # So any fails means Score=0.
    
    if len(fails) == 0:
        print("Score: 1.0")
    else:
        print("Score: 0.0")
        print("First 5 fails:")
        for f in fails[:5]:
            print(f)

