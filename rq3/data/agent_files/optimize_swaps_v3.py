import stim
import sys

def optimize():
    try:
        circuit = stim.Circuit.from_file("baseline.stim")
    except Exception as e:
        print(f"Error loading circuit: {e}")
        return

    ops = []
    
    # Flatten everything to single operations for easier processing
    # We also need to flatten CX to handle SWAP detection.
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append(("CX", [targets[k].value, targets[k+1].value]))
        else:
            targets = instr.targets_copy()
            # For non-CX, we just emit one instruction per target for simplicity of mapping
            # (unless it's a multi-qubit gate other than CX, which baseline doesn't use)
            for t in targets:
                ops.append((instr.name, [t.value]))

    new_ops = []
    
    # orig_map[p] = l means physical wire p holds logical qubit l in the original circuit simulation
    # We start with logical qubit i on wire i.
    orig_map = [i for i in range(36)]
    
    i = 0
    while i < len(ops):
        name, targets = ops[i]
        
        is_swap = False
        if name == "CX":
            # Look ahead for SWAP pattern
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
                        # We skip emitting these gates.
                        # We update orig_map to reflect the swap happened in original circuit.
                        # Original circuit: SWAP u v -> logical content of u and v swapped.
                        orig_map[u], orig_map[v] = orig_map[v], orig_map[u]
                        
                        i += 3
                        is_swap = True
        
        if not is_swap:
            # Emit mapped gate
            # Original: Gate on wire t.
            # Means: Gate on logical qubit orig_map[t].
            # My circuit: Gate on logical qubit orig_map[t].
            # Since my circuit has logical qubit q at wire q (always),
            # we emit Gate on wire orig_map[t].
            
            new_targets = []
            for t in targets:
                new_targets.append(orig_map[t])
            
            new_ops.append((name, new_targets))
            i += 1
            
    # Reconstruct optimized circuit
    new_circ = stim.Circuit()
    for name, targets in new_ops:
        new_circ.append(name, targets)
        
    # Restoration step
    # We want physical k to hold logical orig_map[k].
    # Currently physical k holds logical k.
    # So we need to permute the state such that content[k] becomes orig_map[k].
    
    current_content = [i for i in range(36)] # physical p holds logical p
    restoring_swaps_count = 0
    
    # We want final_content[k] == orig_map[k]
    # We iterate k from 0 to 35.
    # At step k, we ensure physical k holds orig_map[k].
    
    for k in range(36):
        target_logical = orig_map[k]
        
        # Find who currently holds target_logical
        current_loc = -1
        for p in range(36):
            if current_content[p] == target_logical:
                current_loc = p
                break
        
        if current_loc != k:
            # Swap physical k and current_loc
            new_circ.append("CX", [k, current_loc])
            new_circ.append("CX", [current_loc, k])
            new_circ.append("CX", [k, current_loc])
            
            # Update current_content
            # The logical qubit at k (which was content[k]) moves to current_loc.
            # The logical qubit at current_loc (which was target_logical) moves to k.
            
            temp = current_content[k]
            current_content[k] = current_content[current_loc]
            current_content[current_loc] = temp
            
            restoring_swaps_count += 1
            
    print(f"Added {restoring_swaps_count} restoring swaps.")
    
    new_circ.to_file("candidate.stim")
    print("Optimization complete.")

if __name__ == "__main__":
    optimize()
