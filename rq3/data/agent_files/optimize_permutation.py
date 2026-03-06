import stim
import random
import sys

def count_cx(circuit):
    cx = 0
    for op in circuit:
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "CXSWAP", "SWAPCX", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            cx += len(op.targets_copy()) // 2
    return cx

def count_volume(circuit):
    vol = 0
    for op in circuit:
        if op.name in ["QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "SHIFT_COORDS", "TICK"]:
            continue
        targets = op.targets_copy()
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            vol += len(targets) // 2
        else:
            vol += len(targets)
    return vol

def apply_permutation_to_stabilizers(stabilizers, perm):
    # perm maps old_index -> new_index
    # We want to create a new PauliString where the Pauli at new_index comes from old_index
    # So new_stabilizer[new_index] = old_stabilizer[old_index]
    # new_stabilizer[p] = old_stabilizer[perm_inv[p]]
    
    # Or simply:
    # Iterate over old_stabilizer (i, P). Place P at perm[i] in new_string.
    
    num_qubits = len(perm)
    new_stabilizers = []
    
    for s in stabilizers:
        new_s_list = ['I'] * num_qubits
        for i in range(len(s)):
            if i < num_qubits:
                p_val = s[i] # This returns an int or something? 
                # stim.PauliString slicing/indexing gives 0,1,2,3 for I,X,Y,Z
                # But treating as string is easier if we loaded as string
                # But we have PauliString objects.
                # Let's just use string representation if possible or manual construction
                pass
        
        # Easier: work with string representations
        s_str = str(s)
        # s_str might have length != num_qubits if stripped?
        # But we know they are 105 chars
        
        # Check length
        if len(s_str) > num_qubits:
             s_str = s_str[:num_qubits] # Truncate if too long?
        
        for i, char in enumerate(s_str):
            if i in perm:
                new_s_list[perm[i]] = char
        
        new_stabilizers.append(stim.PauliString("".join(new_s_list)))
        
    return new_stabilizers

def relabel_circuit(circuit, perm_inv):
    # perm_inv maps new_index -> old_index
    # The circuit acts on new_indices. We want to map them back to old_indices.
    
    new_circuit = stim.Circuit()
    for op in circuit:
        if op.name in ["QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "SHIFT_COORDS", "TICK"]:
            new_circuit.append(op)
            continue
            
        targets = op.targets_copy()
        new_targets = []
        for t in targets:
            if t.is_qubit_target:
                new_targets.append(perm_inv[t.value])
            else:
                # Handle measurement targets etc if needed, but baseline has none
                new_targets.append(t)
        
        new_circuit.append(op.name, new_targets, op.gate_args_copy())
        
    return new_circuit

def solve():
    print("Loading stabilizers...")
    try:
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\stabilizers.txt", "r") as f:
            stabilizers_lines = [line.strip() for line in f if line.strip()]
        
        stabilizers = [stim.PauliString(s) for s in stabilizers_lines]
        num_qubits = len(stabilizers[0])
        print(f"Num qubits: {num_qubits}")
        
        # Load baseline for metrics
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        base_cx = count_cx(baseline)
        base_vol = count_volume(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        
    except Exception as e:
        print(f"Error: {e}")
        return

    # Strategy: Try random permutations
    # Also try Identity (should match baseline)
    # Also try Reverse
    
    indices = list(range(num_qubits))
    
    best_cx = base_cx
    best_vol = base_vol
    best_circuit = None
    
    attempts = 20 # Try 20 random permutations
    
    # Pre-generate some permutations
    perms = []
    # 1. Identity
    perms.append(dict(zip(indices, indices)))
    # 2. Reverse
    perms.append(dict(zip(indices, reversed(indices))))
    # 3. Random
    for _ in range(attempts):
        shuffled = list(indices)
        random.shuffle(shuffled)
        perms.append(dict(zip(indices, shuffled)))
        
    print(f"Trying {len(perms)} permutations...")
    
    for i, perm in enumerate(perms):
        # perm: old -> new
        # We need to construct new stabilizers.
        
        # Invert perm to map new -> old easily
        perm_inv = {v: k for k, v in perm.items()}
        
        try:
            new_stabilizers_obj = []
            for s in stabilizers:
                # s is a PauliString.
                # Let's get the list of Paulis.
                # s[k] returns the Pauli at index k (0=I, 1=X, 2=Y, 3=Z)
                
                # We want new_s such that new_s[new_idx] = s[old_idx]
                # new_idx ranges from 0 to num_qubits-1
                # old_idx = perm_inv[new_idx]
                
                new_paulis = []
                for new_idx in range(num_qubits):
                    old_idx = perm_inv[new_idx]
                    # Get Pauli at old_idx
                    # stim.PauliString.__getitem__ returns int
                    p_val = s[old_idx]
                    new_paulis.append(p_val)
                    
                # Create PauliString from list of ints? No, need string or other way.
                # stim.PauliString(list_of_ints) works?
                # Let's check docs or try.
                # Actually stim.PauliString(iterable_of_ints) works.
                new_s = stim.PauliString(new_paulis)
                new_stabilizers_obj.append(new_s)

            # 2. Tableau
            tableau = stim.Tableau.from_stabilizers(new_stabilizers_obj, allow_underconstrained=True)

            
            # 3. Synthesize
            # method="elimination" is usually best for CX count
            c = tableau.to_circuit(method="elimination")
            
            # 4. Relabel back
            c_relabeled = relabel_circuit(c, perm_inv)
            
            # 5. Metrics
            cx = count_cx(c_relabeled)
            vol = count_volume(c_relabeled)
            
            # print(f"Perm {i}: CX={cx}, Vol={vol}")
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"IMPROVEMENT FOUND at perm {i}! CX={cx}, Vol={vol}")
                best_cx = cx
                best_vol = vol
                best_circuit = c_relabeled
                
                # Save immediately
                with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq3\\candidate_perm.stim", "w") as f:
                    f.write(str(best_circuit))
                    
        except Exception as e:
            print(f"Error on perm {i}: {e}")
            
    if best_circuit:
        print(f"Final Best: CX={best_cx}, Vol={best_vol}")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    solve()
