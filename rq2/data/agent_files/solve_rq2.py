import stim
import sys
import os

def solve():
    # Load circuit
    with open("input.stim", "r") as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    
    # Identify max qubit index
    max_qubit = 0
    for instr in circuit:
        for t in instr.targets_copy():
            if t.is_qubit_target:
                max_qubit = max(max_qubit, t.value)
    
    next_flag = max_qubit + 1
    
    # Simulation to track state
    sim = stim.TableauSimulator()
    
    # New circuit construction
    new_circuit = stim.Circuit()
    
    # Track accumulated error spread
    # spread_X[q] = number of data qubits affected by X error on q
    # spread_Z[q] = number of data qubits affected by Z error on q
    spread_X = {q: 1 for q in range(max_qubit + 1)}
    spread_Z = {q: 1 for q in range(max_qubit + 1)}
    
    LIMIT = 2 
    
    # Pre-computation of data qubits set for counting
    data_qubits = set(range(max_qubit + 1))
    
    for instr in circuit:
        name = instr.name
        
        if name == "CX":
            targets = instr.targets_copy()
            # Iterate pairs
            for i in range(0, len(targets), 2):
                c = targets[i].value
                t = targets[i+1].value
                
                # Check PRE-conditions? 
                # No, we check post-conditions or accumulate and check.
                # Accumulate spread
                
                # X on c spreads to t
                # spread_X[c] += spread_X[t] ? 
                # No. X_c -> X_c X_t.
                # The set of qubits affected by X_c becomes Union(set_X_c, set_X_t).
                # But X_t is just {t}.
                # So set_X_c += {t}.
                # But what if t is already in set_X_c? 
                # Unlikely in simple spread, but possible.
                # Let's simplify: simply increment count.
                spread_X[c] += 1
                
                # Z on t spreads to c
                # Z_t -> Z_t Z_c
                spread_Z[t] += 1
                
                # Apply CX to simulator and circuit
                op = stim.CircuitInstruction("CX", [targets[i], targets[i+1]])
                new_circuit.append(op)
                sim.do(op)
                
                # Check if we need to flag X on c
                if spread_X[c] >= LIMIT:
                    # Find stabilizer to check X on c
                    # Needs to anticommute with X_c => Has Z or Y on c
                    stabs = sim.canonical_stabilizers()
                    best_S = None
                    min_weight = 9999
                    
                    for s in stabs:
                        p_at_c = s[c]
                        if p_at_c == 2 or p_at_c == 3: # Y or Z
                            w = s.weight
                            if w < min_weight:
                                min_weight = w
                                best_S = s
                            if w == 2: 
                                break
                    
                    if best_S is not None:
                        # Create check gadget
                        flag = next_flag
                        next_flag += 1
                        
                        # Measure S using flag
                        # Prep |+>
                        new_circuit.append(stim.CircuitInstruction("R", [flag]))
                        new_circuit.append(stim.CircuitInstruction("H", [flag]))
                        sim.do(stim.CircuitInstruction("R", [flag]))
                        sim.do(stim.CircuitInstruction("H", [flag]))
                        
                        qubits_indices = [k for k in range(len(best_S)) if best_S[k] != 0]
                        for q in qubits_indices:
                            p = best_S[q]
                            if p == 1: # X
                                op_g = stim.CircuitInstruction("CX", [flag, q])
                            elif p == 2: # Y
                                op_g = stim.CircuitInstruction("CY", [flag, q])
                            elif p == 3: # Z
                                op_g = stim.CircuitInstruction("CZ", [flag, q])
                            new_circuit.append(op_g)
                            sim.do(op_g)
                            
                        # Measure X
                        new_circuit.append(stim.CircuitInstruction("H", [flag]))
                        new_circuit.append(stim.CircuitInstruction("M", [flag]))
                        sim.do(stim.CircuitInstruction("H", [flag]))
                        sim.do(stim.CircuitInstruction("M", [flag]))
                        
                        # Reset spread
                        spread_X[c] = 1
                
                # Check if we need to flag Z on t
                if spread_Z[t] >= LIMIT:
                    # Find stabilizer to check Z on t
                    # Needs to anticommute with Z_t => Has X or Y on t
                    stabs = sim.canonical_stabilizers()
                    best_S = None
                    min_weight = 9999
                    
                    for s in stabs:
                        p_at_t = s[t]
                        if p_at_t == 1 or p_at_t == 2: # X or Y
                            w = s.weight
                            if w < min_weight:
                                min_weight = w
                                best_S = s
                            if w == 2: 
                                break
                                
                    if best_S is not None:
                        # Create check gadget
                        flag = next_flag
                        next_flag += 1
                        
                        new_circuit.append(stim.CircuitInstruction("R", [flag]))
                        new_circuit.append(stim.CircuitInstruction("H", [flag]))
                        sim.do(stim.CircuitInstruction("R", [flag]))
                        sim.do(stim.CircuitInstruction("H", [flag]))
                        
                        qubits_indices = [k for k in range(len(best_S)) if best_S[k] != 0]
                        for q in qubits_indices:
                            p = best_S[q]
                            if p == 1: 
                                op_g = stim.CircuitInstruction("CX", [flag, q])
                            elif p == 2: 
                                op_g = stim.CircuitInstruction("CY", [flag, q])
                            elif p == 3: 
                                op_g = stim.CircuitInstruction("CZ", [flag, q])
                            new_circuit.append(op_g)
                            sim.do(op_g)
                            
                        new_circuit.append(stim.CircuitInstruction("H", [flag]))
                        new_circuit.append(stim.CircuitInstruction("M", [flag]))
                        sim.do(stim.CircuitInstruction("H", [flag]))
                        sim.do(stim.CircuitInstruction("M", [flag]))
                        
                        spread_Z[t] = 1

        else:
            new_circuit.append(instr)
            sim.do(instr)
            
    # Write output
    with open("gen_ft_solution.stim", "w") as f:
        f.write(str(new_circuit))
        
    print(f"Generated circuit with {len(new_circuit)} instructions.")
    print(f"Next flag index: {next_flag}")
    
    # Save ancilla indices
    with open("ancillas.txt", "w") as f:
        # ancillas are from max_qubit + 1 to next_flag - 1
        ancillas = list(range(max_qubit + 1, next_flag))
        f.write(",".join(map(str, ancillas)))

if __name__ == "__main__":
    solve()
