import stim

circuit_str = """H 0 1 2 3 4 5 7 8 10 11 14 17 19 21 23
CX 0 1 0 2 0 3 0 4 0 5 0 7 0 8 0 10 0 11 0 14 0 17 0 19 0 21 0 23 0 42 0 48 42 1 1 42 42 1 1 27 44 2 2 44 44 2 2 27
H 6
CX 6 2 6 3 3 6 6 3
H 9 12 13 15 16 18 20 22
CX 3 9 3 12 3 13 3 15 3 16 3 18 3 20 3 22 3 27 3 33 33 4 4 33 33 4 4 46 12 4 36 4 46 5 5 46 46 5 5 39 12 5 36 5 39 6 6 39 39 6 18 6 36 6 24 7 7 24 24 7 19 7 39 8 8 39 39 8 8 10 8 11 8 14 8 17 8 19 8 21 8 23 8 24 8 27 8 33 8 39 8 42 8 44 8 46 8 48 27 9 9 27 27 9 9 30 27 10 10 27 27 10 10 12 10 13 10 15 10 16 10 18 10 20 10 22 10 30 36 11 11 36 36 11 12 11 15 12 18 13 13 18 18 13 15 13 19 14 14 19 19 14 42 14 42 15 15 42 42 15 15 21 15 23 15 28 15 33 15 36 15 39 15 44 15 46 24 16 16 24 24 16 16 17 16 19 16 27 16 28 16 30 16 48 30 17 17 30 30 17 17 34 18 20 18 22 18 24 18 34 18 42 42 19 19 42 42 19 19 20 19 40 20 40 21 23 21 25 21 44 21 46 33 22 22 33 33 22 22 25 22 28 22 36 22 39 28 23 23 28 28 23 23 31 27 24 24 27 27 24 24 30 24 31 24 34 24 42 24 48 34 25 25 34 34 25 25 37 27 26 26 27 27 26 26 33 26 37 26 40 40 27 27 40 40 27 44 28 28 44 44 28 28 34 28 44 28 46 34 29 29 34 34 29 29 34 39 30 30 39 39 30 30 31 30 34 30 36 31 35 42 32 32 42 42 32 32 35 32 37 32 39 32 48 37 33 33 37 37 33 33 41 37 34 34 37 37 34 34 41 44 35 35 44 44 35 35 40 46 36 36 46 46 36 36 37 36 40 37 42 46 38 38 46 46 38 38 42 38 44 44 39 39 44 44 39 39 46 44 40 40 44 44 40 40 41 40 46 40 48 44 42 42 44 44 42 43 42 44 42 45 42 46 42 47 42 48 42 44 43 45 43 46 43 47 43 48 43 45 44 46 44 47 44 48 44 46 45 47 45 48 45 47 46 48 46 48 47"""

stabilizers = [
"XXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIII", "IIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIII", "IIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIII", "IIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXII", "IIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIII", "IIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXX", "IIIIIIXIIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXIIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIIIIIIXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXIIIIIIXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIIIIIXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIIIIIXIIIIII", "IIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIII", "IZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIII", "IIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIII", "IIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIII", "IIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZI", "IIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIII", "ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIII", "IIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZII", "IIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ"
]

data_qubits = list(range(49))

def analyze_circuit():
    circuit = stim.Circuit(circuit_str)
    
    # 1. Stabilizer check
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    for s in stabilizers:
        p = stim.PauliString(s)
        if sim.peek_observable_expectation(p) == 1:
            preserved += 1
    print(f"Stabilizers preserved: {preserved}/{len(stabilizers)}")

    # 2. Fault tolerance check
    ops = []
    # Flatten properly - use basic iteration since circuit is flat
    for op in circuit:
        if op.name in ["H", "CX"]:
            ops.append(op)
    
    # Simple symplectic simulator
    bad_faults = []
    
    # We simulate fault at instruction i
    for i in range(len(ops)):
        op = ops[i]
        targs = []
        if op.name == "H":
            targs = [t.value for t in op.targets_copy()]
        elif op.name == "CX":
            targs = [t.value for t in op.targets_copy()]
        
        qubits_in_op = sorted(list(set(targs)))
        
        for q_fault in qubits_in_op:
            for p_type in ["X", "Z"]: # Y is effectively X+Z
                # Initial error state: dict {qubit: (x, z)}
                error_state = {} 
                error_state[q_fault] = (1, 0) if p_type == "X" else (0, 1)
                
                # Propagate
                for j in range(i+1, len(ops)):
                    op_j = ops[j]
                    if op_j.name == "H":
                        for t in op_j.targets_copy():
                            qv = t.value
                            if qv in error_state:
                                (x, z) = error_state[qv]
                                error_state[qv] = (z, x)
                    elif op_j.name == "CX":
                        ts = op_j.targets_copy()
                        for k in range(0, len(ts), 2):
                            c = ts[k].value
                            t = ts[k+1].value
                            
                            (xc, zc) = error_state.get(c, (0,0))
                            (xt, zt) = error_state.get(t, (0,0))
                            
                            # CNOT: Xc -> Xc Xt, Zt -> Zc Zt
                            new_xc = xc
                            new_xt = (xt + xc) % 2
                            new_zc = (zc + zt) % 2
                            new_zt = zt
                            
                            if new_xc or new_zc: error_state[c] = (new_xc, new_zc)
                            elif c in error_state: del error_state[c]

                            if new_xt or new_zt: error_state[t] = (new_xt, new_zt)
                            elif t in error_state: del error_state[t]
                
                # Count weight
                # Map error to pauli string
                # We need to preserve indices
                p_chars = ["_"] * 49
                weight = 0
                for dq in data_qubits:
                    if dq in error_state:
                        (x, z) = error_state[dq]
                        if x and z: 
                            p_chars[dq] = "Y"
                            weight += 1
                        elif x: 
                            p_chars[dq] = "X"
                            weight += 1
                        elif z: 
                            p_chars[dq] = "Z"
                            weight += 1
                
                # If weight >= 3, check if reducible
                final_weight = weight
                
                if weight >= 3:
                    # Init stabilizers if needed
                    if not hasattr(analyze_circuit, "stab_objs"):
                        analyze_circuit.stab_objs = [stim.PauliString(s.replace("I", "_")) for s in stabilizers]
                    
                    p_str = "".join(p_chars)
                    current_p = stim.PauliString(p_str)
                    
                    # Greedy reduction
                    changed = True
                    while changed and final_weight >= 3:
                        changed = False
                        best_local_w = final_weight
                        best_local_p = current_p
                        
                        for s in analyze_circuit.stab_objs:
                            prod = current_p * s
                            # Get weight of product
                            # str(prod) starts with + or -
                            s_prod = str(prod)[1:] 
                            w = len(s_prod) - s_prod.count("_")
                            
                            if w < best_local_w:
                                best_local_w = w
                                best_local_p = prod
                                changed = True
                                # Optimization: if < 3, break early
                                if w < 3: break
                        
                        if changed:
                            current_p = best_local_p
                            final_weight = best_local_w
                
                if final_weight >= 3:
                    # Store the PauliString for cover analysis
                    # We need the ACTUAL error string on data qubits
                    bad_faults.append(current_p)
                    # print(f"Op {i} {op.name}: Fault {p_type} on {q_fault} -> Weight {final_weight}")

    print(f"Bad faults count: {len(bad_faults)}")
    
    # 3. Find covering set of stabilizers
    if bad_faults:
        if not hasattr(analyze_circuit, "stab_objs"):
             analyze_circuit.stab_objs = [stim.PauliString(s.replace("I", "_")) for s in stabilizers]
        
        # Build coverage map
        # fault_index -> set of stabilizer_indices that detect it
        coverage = []
        for pid, p in enumerate(bad_faults):
            detectors = set()
            for sid, s in enumerate(analyze_circuit.stab_objs):
                if not p.commutes(s):
                    detectors.add(sid)
            coverage.append(detectors)
            
        # Check if any fault is undetectable
        undetectable = [i for i, c in enumerate(coverage) if not c]
        if undetectable:
            print(f"WARNING: {len(undetectable)} faults are undetectable (commute with all stabilizers)!")
            # These might be logical errors or harmless weight 3 stabilizers?
            # If they commute with all, they are in N(S).
            # N(S) = S U L.
            # If S, we reduced weight. If still >=3, then it's a "heavy stabilizer"?
            # Or a logical operator.
            pass
            
        # Greedy set cover
        # Universe: all fault indices (that are detectable)
        universe = set(range(len(bad_faults))) - set(undetectable)
        chosen_stabilizers = []
        
        while universe:
            # Find stabilizer that covers most remaining faults
            best_s = -1
            best_cover_count = -1
            
            for sid in range(len(stabilizers)):
                if sid in chosen_stabilizers: continue
                
                # Count how many of 'universe' are covered by 'sid'
                count = 0
                for fid in universe:
                    if sid in coverage[fid]:
                        count += 1
                
                if count > best_cover_count:
                    best_cover_count = count
                    best_s = sid
            
            if best_cover_count <= 0:
                print("Cannot cover remaining faults!")
                break
                
            chosen_stabilizers.append(best_s)
            # Remove covered
            to_remove = []
            for fid in universe:
                if best_s in coverage[fid]:
                    to_remove.append(fid)
            for fid in to_remove:
                universe.remove(fid)
        
        print(f"Chosen {len(chosen_stabilizers)} stabilizers to measure:")
        print(chosen_stabilizers)
        
        # Verify cover
        # Double check? No need.

if __name__ == "__main__":
    analyze_circuit()
