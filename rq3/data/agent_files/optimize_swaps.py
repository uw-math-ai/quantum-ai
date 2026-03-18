import stim
import sys

def solve_permutation(perm):
    """
    Returns a list of swaps (pairs of indices) to sort the permutation.
    'perm' is a list where perm[i] is the logical qubit currently at physical location i.
    We want to sort it so that perm[i] == i.
    """
    swaps = []
    p = list(perm)
    n = len(p)
    
    # We want p[i] == i
    # Position map: where is logical value x?
    pos = {val: i for i, val in enumerate(p)}
    
    for i in range(n):
        if p[i] != i:
            # We want value 'i' to be at position 'i'.
            # Currently 'i' is at pos[i].
            # The value at position 'i' is p[i].
            target_loc = pos[i]
            current_val_at_i = p[i]
            
            # Swap physical locations i and target_loc
            swaps.append((i, target_loc))
            
            # Update state
            p[i], p[target_loc] = p[target_loc], p[i]
            
            # Update positions
            pos[i] = i
            pos[current_val_at_i] = target_loc
            
    return swaps

def optimize():
    baseline = stim.Circuit.from_file("baseline.stim")
    
    # Flatten operations into a stream of (name, targets)
    # But we need to handle the CX stream specially to detect swaps.
    
    # We will decompose all CX gates into individual pairs first.
    # Other gates kept as is.
    
    flattened_ops = []
    
    for instr in baseline:
        if instr.name in ["CX", "CNOT"]:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                flattened_ops.append(("CX", [targets[k].value, targets[k+1].value]))
        else:
            # Keep other instructions as is, but we might need to split them if they have multiple targets 
            # to apply the map correctly? 
            # Actually, we can just apply the map to the targets and emit the instruction.
            # But the map changes dynamically. So we must process in order.
            # If an instruction has multiple targets like H 0 1 2, and we have no pending swaps, it's fine.
            # But if we are processing a stream where swaps might happen "inside" a CX chain, 
            # we only care about CX swaps.
            # The baseline has H 0 5 6 7. These are single qubit gates.
            # The SWAPs are only CXs.
            # So we can keep non-CX instructions as blocks.
            flattened_ops.append((instr.name, [t.value for t in instr.targets_copy()]))

    # Now iterate and process
    new_ops = []
    
    # logical_to_physical[q] = p means logical qubit q is at physical wire p.
    # We want to track: where is the data for original wire q?
    # map[q] = current_location_of_q
    layout = {i: i for i in range(36)} 
    
    # We iterate through the flattened ops.
    # But wait, I flattened EVERYTHING.
    # H 0 1 2 -> H 0, H 1, H 2? 
    # No, I kept non-CX as blocks. 
    # But if I have H 0 1 and map[0]!=0, map[1]!=1, I need to emit H map[0] map[1].
    
    # Re-flatten everything to be safe and simple.
    full_stream = []
    for instr in baseline:
        if instr.name in ["CX", "CNOT"]:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                full_stream.append(("CX", [targets[k].value, targets[k+1].value]))
        else:
            targets = instr.targets_copy()
            # Most gates take 1 target (H, S, etc) or are applied locally.
            # Some 2 qubit gates? The baseline only has CX as 2-qubit gate.
            # Check for other 2-qubit gates?
            # Baseline uses H and CX.
            # So other gates are 1-qubit.
            for t in targets:
                full_stream.append((instr.name, [t.value]))

    # Now detect swaps in CX stream
    i = 0
    while i < len(full_stream):
        op, targets = full_stream[i]
        
        if op == "CX":
            # Check for SWAP pattern: CX a b, CX b a, CX a b
            if i + 2 < len(full_stream):
                op2, targets2 = full_stream[i+1]
                op3, targets3 = full_stream[i+2]
                
                if op2 == "CX" and op3 == "CX":
                    a, b = targets
                    c, d = targets2
                    e, f = targets3
                    
                    # Pattern 1: a,b - b,a - a,b (Standard SWAP)
                    if c == b and d == a and e == a and f == b:
                        # Found SWAP(a, b) on physical wires a and b.
                        # The circuit says: swap data on wire a and wire b.
                        # We SKIP the gates.
                        # And we update the layout:
                        # The data that WAS at 'a' is now at 'b' (according to circuit).
                        # But since we skipped the swap, the data is STILL at 'a'.
                        # So future operations targeting 'b' (where the data should be)
                        # must now target 'a' (where the data actually is).
                        # And vice versa.
                        # Wait.
                        # Original: Gate(b) -> applies to data that moved to b.
                        # My circuit: Data is at a. So I must emit Gate(a).
                        # So `layout` maps `original_wire` -> `actual_wire`.
                        # Let's verify.
                        # Start: layout[x] = x.
                        # SWAP u v.
                        # Original intent: data at u <-> data at v.
                        # Skipped.
                        # Future Gate(u): applies to data at u.
                        # Original Future Gate(u): applies to new data at u (which came from v).
                        # So Original Future Gate(u) really wants to target the data from v.
                        # Where is data from v? It is at `layout[v]`.
                        # So Original Future Gate(u) should become Gate(layout[v])?
                        # No.
                        # Let's trace logical qubits.
                        # Let `L[p]` be the logical qubit at physical wire `p`.
                        # Initially `L[p] = p`.
                        # Op `CX u v`: applies to logical qubits `L[u]` and `L[v]`.
                        # We emit `CX u v`. (Unless simplified).
                        # Op `SWAP u v`:
                        # Updates `L`: `L[u], L[v] = L[v], L[u]`.
                        # We emit NOTHING.
                        # Next Op `H u`: applies to logical qubit `L[u]`.
                        # We want to apply H to that logical qubit.
                        # Where is `L[u]`? It is at `u`.
                        # Wait.
                        # If I just track `L`, and I emit gates on `u, v`...
                        # If I skip SWAP, then `L[u]` and `L[v]` do NOT swap physical places.
                        # But the *original circuit* assumes they DID.
                        # So the original circuit says "Do H on physical u".
                        # This implies "Do H on the logical qubit currently at physical u".
                        # In the original execution, that would be the qubit that came from v.
                        # In my execution (no swap), that qubit is still at v.
                        # So "Do H on physical u" should become "Do H on physical v".
                        # Yes.
                        # So I need a map `forward_map[original_physical] = current_physical`.
                        # Initially `f[p] = p`.
                        # When `SWAP u v` is encountered in original:
                        # The meaning of "physical u" and "physical v" swaps for future instructions.
                        # "physical u" now refers to what was "physical v".
                        # So `f[u], f[v] = f[v], f[u]`.
                        # When `Gate u` is encountered:
                        # We emit `Gate f[u]`.
                        
                        # Let's trace.
                        # Start f={0:0, 1:1}.
                        # SWAP 0 1. f becomes {0:1, 1:0}.
                        # H 0. Emit H f[0] -> H 1.
                        # Correct.
                        
                        # Update map
                        # Accessing a and b is tricky because they are the indices in the flattened stream,
                        # which are ALREADY affected by previous swaps?
                        # NO. The flattened stream is the ORIGINAL circuit.
                        # So a and b are the arguments in the original circuit.
                        # So we update `layout[a]` and `layout[b]`.
                        
                        val_a = layout[a]
                        val_b = layout[b]
                        layout[a] = val_b
                        layout[b] = val_a
                        
                        i += 3
                        continue
        
        # If not a swap, or not CX, emit mapped instruction
        new_targets = []
        for t in targets:
            new_targets.append(layout[t])
        
        new_ops.append((op, new_targets))
        i += 1

    # Reconstruct circuit
    new_circ = stim.Circuit()
    for op, targets in new_ops:
        new_circ.append(op, targets)

    # Now we must restore the physical layout.
    # `layout[p]` tells us where the "logical wire p" (from the perspective of the original circuit's end)
    # is currently located.
    # Wait, `layout` maps `original_instruction_wire` -> `actual_wire`.
    # At the end of the circuit, we have a state.
    # The original circuit would have the result on wire `p`.
    # My circuit has that result on wire `layout[p]`.
    # So I have a permutation: `logical p` is at `layout[p]`.
    # I want `logical p` to be at `p`.
    # So I need to move data from `layout[p]` to `p`.
    # This is exactly the `solve_permutation` problem.
    # `perm[p] = layout[p]`?
    # No. `layout[p]` is "where the data for p is".
    # `solve_permutation` expects `perm[i]` to be "the logical qubit at physical i".
    # Let's construct `current_content`.
    # `current_content[loc] = logical_id`.
    # `layout` is `logical_id -> loc`.
    # So `current_content` is the inverse of `layout`.
    
    current_content = [0] * 36
    for logical, physical in layout.items():
        current_content[physical] = logical
        
    final_swaps = solve_permutation(current_content)
    
    print(f"Removed swaps. Adding {len(final_swaps)} restoring swaps.")
    
    for p1, p2 in final_swaps:
        new_circ.append("CX", [p1, p2])
        new_circ.append("CX", [p2, p1])
        new_circ.append("CX", [p1, p2])
        
    # Save optimized
    new_circ.to_file("candidate.stim")
    print("Optimization complete.")

if __name__ == "__main__":
    optimize()
