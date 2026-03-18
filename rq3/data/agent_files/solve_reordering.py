import stim
import random
import copy

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CZ"]:
            count += len(instr.targets_copy()) // 2
        elif instr.name == "SWAP":
            count += 3 * (len(instr.targets_copy()) // 2)
    return count

def relabel_circuit(circuit, mapping):
    # mapping: old_index -> new_index
    # We want to apply this mapping to all gate targets
    new_circuit = stim.Circuit()
    for instr in circuit:
        targets = instr.targets_copy()
        new_targets = []
        for t in targets:
            if t.is_qubit_target:
                # Just append the new qubit index
                new_targets.append(mapping[t.value])
            else:
                new_targets.append(t)
        new_circuit.append(instr.name, new_targets, instr.gate_args_copy())
    return new_circuit

def get_inverse_mapping(mapping):
    # mapping is list where index i maps to value mapping[i]
    # inverse: value v maps to index where mapping[index] == v
    inv = [0] * len(mapping)
    for i, v in enumerate(mapping):
        inv[v] = i
    return inv

def solve():
    # Load baseline
    with open("my_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    with open("my_stabilizers.txt", "r") as f:
        stabs = [l.strip() for l in f if l.strip()]
        
    base_cx = count_cx(baseline)
    print(f"Baseline CX: {base_cx}")
    
    # Tableau
    tableau = stim.Tableau.from_circuit(baseline)
    n_qubits = len(tableau)
    print(f"N qubits: {n_qubits}")
    
    # Try random permutations
    best_cx = base_cx
    best_circuit = baseline
    
    # Heuristic: Try to order qubits by "activity" in stabilizers?
    # Or just random.
    attempts = 500 # Fast enough
    
    for i in range(attempts):
        # Create a permutation of 0..n-1
        perm = list(range(n_qubits))
        random.shuffle(perm)
        
        # Apply permutation to Tableau columns (qubits)
        # T' maps Z_k to ...
        # Actually, stim doesn't have "permute columns" method directly on Tableau.
        # But we can relabel the stabilizers?
        # If we permute qubits, we permute the Pauli strings.
        
        # Easier way:
        # 1. Synthesize circuit C from original T (we know this gives 88 CX).
        # 2. But we want to CHANGE the synthesis order.
        # The `to_circuit` method doesn't take an order argument.
        # But `to_circuit` likely processes qubits 0..N.
        # So if we permute the tableau indices such that "easy" qubits are first/last?
        
        # Correct approach:
        # 1. Define permutation P (old -> new).
        # 2. Create new Tableau T_new where qubit k in T_new corresponds to P(k) in T.
        #    This means T_new's stabilizers are P(T's stabilizers).
        # 3. Synthesize C_new from T_new.
        # 4. Relabel C_new by P_inverse to get circuit on original qubits.
        
        # Construct T_new
        # T_new stabilizers = permuted stabilizers of T
        # How to permute tableau?
        # T has operations x_output(k), z_output(k).
        # We need a fresh tableau from stabilizers?
        # Yes.
        
        # Get stabilizers of T
        # tableau.z_output(k) gives the image of Z_k, which is the k-th stabilizer
        current_stabs = [tableau.z_output(k) for k in range(n_qubits)]
        
        # Permute them
        new_stabs = []
        for s in current_stabs:
            # s is PauliString. Permute its indices.
            # s[k] moves to s[perm[k]]? 
            # No. If we view the qubit i as moving to position perm[i].
            # Then the Pauli at i moves to perm[i].
            
            # Efficient way:
            new_p = stim.PauliString(n_qubits)
            for k in range(n_qubits):
                # old qubit k moves to new position perm[k]
                # So at new position perm[k], we put the Pauli that was at k.
                gate = s[k] # 0=I, 1=X, 2=Y, 3=Z
                if gate == 1: new_p[perm[k]] = "X"
                elif gate == 2: new_p[perm[k]] = "Y"
                elif gate == 3: new_p[perm[k]] = "Z"
            new_stabs.append(new_p)
            
        # Create Tableau from new stabilizers
        # Note: from_stabilizers might fail if underconstrained?
        try:
            # We must use from_stabilizers.
            # But stim.Tableau.from_stabilizers takes a list of PauliStrings.
            # And it returns a tableau that maps Z basis to these stabilizers.
            T_new = stim.Tableau.from_stabilizers(new_stabs)
        except Exception as e:
            # Maybe inconsistent or something? Should not be if permutation is valid.
            continue
            
        # Synthesize
        C_new = T_new.to_circuit()
        
        # Check cost
        c_cx = count_cx(C_new)
        
        if c_cx < best_cx:
            # Relabel back
            # We mapped old k -> new perm[k].
            # So in C_new, qubit q corresponds to old qubit where perm[old] == q.
            # So we map q -> inv_perm[q].
            inv_perm = get_inverse_mapping(perm)
            C_final = relabel_circuit(C_new, inv_perm)
            
            print(f"Found better: {c_cx} CX (Attempt {i})")
            best_cx = c_cx
            best_circuit = C_final
            
            # Verify stabilizers
            sim = stim.TableauSimulator()
            sim.do_circuit(C_final)
            valid = True
            for s_str in stabs:
                # Need to convert string to PauliString
                target_p = stim.PauliString(s_str)
                if sim.peek_observable_expectation(target_p) != 1:
                    valid = False
                    break
            if valid:
                print("  -> Valid!")
                with open("best_candidate.stim", "w") as f:
                    f.write(str(best_circuit))
            else:
                print("  -> Invalid (relabeling bug?)")

solve()
