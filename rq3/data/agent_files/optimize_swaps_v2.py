import stim

def solve_restoration(layout, num_qubits):
    """
    layout: logical_qubit -> physical_qubit
    Returns list of physical swaps (u, v) to restore layout to identity.
    """
    swaps = []
    
    # content: physical_qubit -> logical_qubit
    content = [None] * num_qubits
    for l, p in layout.items():
        content[p] = l
        
    # We want content[i] == i for all i
    
    # Position of each logical qubit
    # logical_pos[x] is the physical location of logical qubit x
    logical_pos = list(layout.values()) # This might be wrong order if keys not sorted
    logical_pos = [layout[i] for i in range(num_qubits)]
    
    for i in range(num_qubits):
        if content[i] != i:
            # We want logical 'i' to be at physical 'i'.
            # Currently logical 'i' is at 'logical_pos[i]'.
            current_loc = logical_pos[i]
            
            # The physical qubit at 'i' currently holds logical 'content[i]'.
            occupant = content[i]
            
            if current_loc != i:
                # Swap physical 'i' and 'current_loc'
                swaps.append((i, current_loc))
                
                # Update our state
                # The logical qubit 'i' moves to 'i'
                # The logical qubit 'occupant' moves to 'current_loc'
                
                content[i] = i
                content[current_loc] = occupant
                
                logical_pos[i] = i
                logical_pos[occupant] = current_loc
                
    return swaps

def optimize():
    circuit = stim.Circuit.from_file("baseline.stim")
    ops = []
    
    # Flatten everything to single operations for easier processing
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append(("CX", [targets[k].value, targets[k+1].value]))
        else:
            targets = instr.targets_copy()
            for t in targets:
                ops.append((instr.name, [t.value]))

    new_ops = []
    layout = {i: i for i in range(36)}
    
    i = 0
    while i < len(ops):
        name, targets = ops[i]
        
        # Check for SWAP pattern
        is_swap = False
        if name == "CX":
            if i + 2 < len(ops):
                name2, targets2 = ops[i+1]
                name3, targets3 = ops[i+2]
                
                if name2 == "CX" and name3 == "CX":
                    u, v = targets
                    u2, v2 = targets2
                    u3, v3 = targets3
                    
                    # Pattern: CX u v, CX v u, CX u v
                    if u == v2 and v == u2 and u == u3 and v == v3:
                        # Found SWAP(u, v)
                        # Update layout: swap where u and v point
                        # layout[u] is physical loc of u
                        # layout[v] is physical loc of v
                        # After swap, logical u is where logical v was (physically) ?? NO
                        # The circuit says "SWAP wires u and v".
                        # This means the logical content of u and v are exchanged.
                        # So logical u is now at physical layout[v].
                        # Logical v is now at physical layout[u].
                        
                        # But wait. My layout tracks "where is logical u".
                        # Start: logical u at u.
                        # Circuit: SWAP u v.
                        # End: logical u at v.
                        # So layout[u] becomes v.
                        # So we swap layout[u] and layout[v].
                        
                        # Wait, layout stores physical locations.
                        # layout[u] = p means logical u is at physical p.
                        # If circuit says SWAP u v (the wires), it means logical u moves to wire v?
                        # No. It means logical content on wire u and wire v are swapped.
                        # Let L[p] be the logical content at physical p.
                        # SWAP u v means L[u] <-> L[v].
                        # Since we want to update `layout` (inverse of L), we just look at what changed.
                        # If L[u] = A, L[v] = B.
                        # New: L[u] = B, L[v] = A.
                        # So logical A is now at v. logical B is now at u.
                        # Before: logical A at u, logical B at v.
                        # So `layout[A]` changes from u to v.
                        # `layout[B]` changes from v to u.
                        # BUT we don't know A and B easily.
                        # We only know layout.
                        
                        # Actually, `layout` maps `logical_initial_wire_index` to `current_physical_wire`.
                        # If the circuit says `SWAP u v`, it means "Swap the contents of wire u and wire v".
                        # This operation is on the *wires*.
                        # So whatever logical qubit was at wire u moves to wire v.
                        # whatever logical qubit was at wire v moves to wire u.
                        # So for all logical qubits `q`, if `layout[q] == u`, it becomes `v`.
                        # If `layout[q] == v`, it becomes `u`.
                        
                        # So I need to find which logical qubits are at u and v.
                        # Let `inv_layout` be the inverse map.
                        # `inv_layout[u]` is the logical qubit at physical u.
                        # `inv_layout[v]` is the logical qubit at physical v.
                        # We update `layout`:
                        # `layout[inv_layout[u]] = v`
                        # `layout[inv_layout[v]] = u`
                        
                        # But wait.
                        # This is correct ONLY if we *perform* the swap physically.
                        # Here I am *skipping* the swap physically.
                        # So the data *remains* at u and v physically.
                        # BUT the circuit *thinks* they swapped.
                        # So subsequent operations on `u` (wire u) should apply to the data that is now at `u`.
                        # Since I skipped the swap, the data at `u` is the *original* data at `u`.
                        # The circuit expects data at `u` to be the data that came from `v`.
                        # This is getting confusing.
                        
                        # Let's reset.
                        # My new circuit will be a sequence of operations on physical wires.
                        # I maintain a map `logical_to_physical`.
                        # Initially `l2p[q] = q`.
                        # This means logical qubit q is at physical wire q.
                        
                        # When the original circuit has `Gate(u)`:
                        # It means "Apply Gate to the logical qubit currently at wire u".
                        # Let that logical qubit be `q`.
                        # In my new circuit, `q` is located at `l2p[q]`.
                        # So I should emit `Gate(l2p[q])`.
                        
                        # How do I know which `q` is at `u` in the original circuit?
                        # I need to track the state of the *original* circuit simulation too.
                        # Let `orig_wire_to_logical[u]` be the logical qubit at wire u in the original circuit.
                        # Initially `orig[u] = u`.
                        # When original circuit says `SWAP u v`:
                        # `orig[u], orig[v] = orig[v], orig[u]`.
                        # My circuit does NOTHING (skips).
                        # So `l2p` does not change.
                        
                        # When original circuit says `Gate(u)`:
                        # The logical qubit affected is `q = orig[u]`.
                        # My circuit needs to apply Gate to `q`.
                        # Where is `q` in my circuit? `l2p[q]`.
                        # So emit `Gate(l2p[q])`.
                        
                        # This is much cleaner!
                        # `orig_wire_to_logical` tracks the "virtual" swaps in the baseline.
                        # `l2p` tracks the "actual" location of logical qubits in my optimized circuit.
                        # Since I skip swaps, `l2p` never changes!
                        # `l2p` stays identity!
                        # So I emit `Gate(l2p[orig[u]])` -> `Gate(orig[u])`.
                        # Wait. If `l2p` is identity, then `Gate(orig[u])` is applied to physical wire `orig[u]`.
                        # Is `orig[u]` the correct physical wire?
                        # Yes, because `l2p` is identity means logical `q` is at physical `q`.
                        # So if we want to target logical `q`, we target physical `q`.
                        # So the rule is:
                        # 1. Track `orig_map` (wire -> logical). Init identity.
                        # 2. On `SWAP u v` in original: update `orig_map`: swap u and v contents. Emit nothing.
                        # 3. On `Gate u` in original: `q = orig_map[u]`. Emit `Gate q`.
                        # 4. At the end, we have a set of logical qubits at physical locations `l2p` (identity).
                        # BUT the *original* circuit ended with logical qubits at `orig_map_final`.
                        # The stabilizers are defined on the *physical output wires*.
                        # The stabilizers expect the data that *should have been* at wire `k` (in original) to be tested by stabilizer `S_k`.
                        # Wait. Stabilizers are defined on wires 0..35.
                        # Stabilizer `S` on wire `k` checks the qubit at wire `k`.
                        # In the original circuit, wire `k` holds logical qubit `orig_map_final[k]`.
                        # In my circuit, wire `k` holds logical qubit `k` (since `l2p` is identity).
                        # So if `orig_map_final[k] != k`, the logical content at wire `k` is different!
                        # The stabilizer `S` expects to see logical qubit `orig_map_final[k]`.
                        # But it sees logical qubit `k`.
                        # So I must permute the qubits at the end so that wire `k` holds logical qubit `orig_map_final[k]`.
                        # Currently wire `k` holds `k`.
                        # I want wire `k` to hold `orig_map_final[k]`.
                        # So I need to move `orig_map_final[k]` to `k`.
                        # Currently `orig_map_final[k]` is at wire `orig_map_final[k]` (since `l2p` is identity).
                        # So I need to move data from `orig_map_final[k]` to `k`.
                        # Let `target_content[k] = orig_map_final[k]`.
                        # I have `current_content[k] = k`.
                        # I want `new_content[k] = target_content[k]`.
                        # This is a permutation.
                        # `P(k) = orig_map_final[k]`.
                        # I need to implement `P` such that `P` maps `k` to `orig_map_final[k]`?
                        # No.
                        # Let's say `orig_map[0] = 1`. (Original circuit put logical 1 at wire 0).
                        # My circuit has logical 1 at wire 1.
                        # Stabilizer 0 checks wire 0. It expects logical 1.
                        # My wire 0 has logical 0.
                        # So I need to move logical 1 to wire 0.
                        # Logical 1 is at wire 1.
                        # So I need `SWAP 0 1`.
                        # Then wire 0 has logical 1. Wire 1 has logical 0.
                        # Correct.
                        
                        # So I need to permute my state (where `q` is at `q`)
                        # into the state defined by `orig_map_final` (where `q` is at `inv_orig_map[q]`).
                        # Wait.
                        # `orig_map[k]` is the logical qubit at wire `k`.
                        # So I want logical `orig_map[k]` to be at wire `k`.
                        # Currently logical `orig_map[k]` is at wire `orig_map[k]`.
                        # So I need to move data from `orig_map[k]` to `k`.
                        # This is exactly `solve_permutation` where `perm[k] = orig_map[k]`.
                        # `perm[k]` is "value at k". I want it to be "value at k in target".
                        # Wait.
                        # I have data `D_0, D_1, ...` at wires `0, 1, ...`.
                        # I want data `D_{orig[0]}, D_{orig[1]}, ...` at wires `0, 1, ...`.
                        # So I want to move `D_{orig[k]}` to `k`.
                        # `D_{orig[k]}` is currently at `orig[k]`.
                        # So I need to move from `orig[k]` to `k`.
                        # This is the permutation `p -> orig[p]`? Or `orig[p] -> p`?
                        # `orig[k]` moves to `k`.
                        # So this is the inverse of `orig`.
                        # But `solve_permutation` takes `perm` such that `perm[i]` is the value at `i`.
                        # And sorts it so `perm[i] == i`?
                        # No. `solve_permutation` (my previous function) sorted `p[i]` to `i`.
                        # Here I have `current[p] = p`.
                        # I want `final[p] = orig[p]`.
                        # This is "unsorting" or applying a permutation.
                        # Applying permutation `sigma` moves item at `i` to `sigma(i)`.
                        # Here item at `orig[k]` moves to `k`.
                        # So `sigma(orig[k]) = k`.
                        # So `sigma` is the inverse of `orig`.
                        # But `orig` is a map `wire -> logical`.
                        # So `sigma` maps `logical -> wire`.
                        # So I need to implement the permutation `inv_orig`.
                        # I can implement any permutation using swaps.
                        
                        # Let's use `solve_permutation` logic but adapted.
                        # `current_layout = {i: i for i in range(N)}`. (Logical i is at physical i).
                        # `target_layout = {orig[k]: k for k in range(N)}`. (Logical orig[k] should be at k).
                        # We want to transform current to target.
                        # Algorithm:
                        # Iterate `k` from 0 to N-1.
                        # We want physical `k` to hold `target_logical = orig[k]`.
                        # Currently physical `k` holds `current_logical = current_layout_inv[k]`.
                        # Find where `target_logical` is. `loc = current_layout[target_logical]`.
                        # If `loc != k`:
                        #   Swap physical `k` and `loc`.
                        #   Update `current_layout`:
                        #     `current_layout[current_logical]` becomes `loc`.
                        #     `current_layout[target_logical]` becomes `k`.
                        #     `current_layout_inv` updates accordingly.
                        #   Emit `SWAP k loc`.
                        
                        # Correct.
                        
                        orig_map[u], orig_map[v] = orig_map[v], orig_map[u]
                        i += 3
                        is_swap = True
        
        if not is_swap:
            # Emit mapped gate
            # target `t` -> `orig_map[t]`?
            # NO.
            # Original: Gate on wire t.
            # Meaning: Gate on logical qubit `orig_map[t]`.
            # My circuit: Gate on logical qubit `orig_map[t]`.
            # Where is logical qubit `orig_map[t]`?
            # Since `l2p` is identity, it is at physical wire `orig_map[t]`.
            # So emit `Gate orig_map[t]`.
            
            new_targets = []
            for t in targets:
                new_targets.append(orig_map[t])
            
            new_ops.append((name, new_targets))
            i += 1
            
    # Reconstruct
    new_circ = stim.Circuit()
    for name, targets in new_ops:
        new_circ.append(name, targets)
        
    # Add restoring swaps
    # current_layout[l] = l
    # target_layout[l] = inv_orig_map[l]  (where l should be)
    # Actually, iterate physical wires.
    # We want physical k to hold orig_map[k].
    
    current_content = [i for i in range(36)] # physical p holds logical p
    # We want physical p to hold orig_map[p]
    
    restoring_swaps = []
    
    for k in range(36):
        target_logical = orig_map[k]
        
        # Who is currently at k?
        current_logical = current_content[k]
        
        if current_logical != target_logical:
            # Find where target_logical is
            # We can scan current_content
            loc = -1
            for p in range(36):
                if current_content[p] == target_logical:
                    loc = p
                    break
            
            # Swap k and loc
            restoring_swaps.append((k, loc))
            current_content[k] = target_logical
            current_content[loc] = current_logical
            
    print(f"Adding {len(restoring_swaps)} restoring swaps.")
    for u, v in restoring_swaps:
        new_circ.append("CX", [u, v])
        new_circ.append("CX", [v, u])
        new_circ.append("CX", [u, v])
        
    new_circ.to_file("candidate.stim")
    print("Optimization complete.")

if __name__ == "__main__":
    optimize()
