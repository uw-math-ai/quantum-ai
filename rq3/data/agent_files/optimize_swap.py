import stim
import collections

def main():
    # Load baseline
    circuit = stim.Circuit.from_file("data/agent_files/candidate_perm.stim")
    
    # Parse into operations, decomposing SWAPs
    # We need to detect "CX a b CX b a CX a b" sequences.
    
    # First, flatten.
    flat_ops = []
    for op in circuit.flattened():
        if op.name == "CX" or op.name == "CNOT":
            # Handle multiple targets in one instruction
            targets = op.targets_copy()
            for i in range(0, len(targets), 2):
                flat_ops.append(("CX", targets[i].value, targets[i+1].value))
        else:
            # Other gates
            # targets can be many
            for t in op.targets_copy():
                flat_ops.append((op.name, t.value))
                
    # Now scan for SWAP patterns
    # Pattern: CX u v, CX v u, CX u v
    # This requires 3 consecutive CX gates on the same pair (u,v).
    # BUT there might be other gates in between that act on OTHER qubits.
    # So we need a DAG or simply filter for gates on u and v.
    
    # Actually, simpler: just iterate and check if next gates on u/v match.
    # But "next gate" on u might be far away if u is idle.
    # So we need to look ahead.
    
    # Let's try a greedy approach.
    # Reconstruct the circuit, tracking the "virtual" SWAPs.
    
    optimized_ops = []
    wire_map = {i: i for i in range(circuit.num_qubits)} # Logical (code) -> Physical
    
    # Wait, for the optimization to work, I need to identify the SWAPs *before* re-mapping.
    # Because the SWAPs in the code are explicit gates.
    # "CX 30 1", "CX 1 30", "CX 30 1".
    # If I identify this triplet, I replace it with a map update.
    
    # To identify triplets efficiently:
    # I can iterate through the operations.
    # If I see CX u v, I look ahead to see if the NEXT operation on u and v is CX v u, and then CX u v.
    # And crucially, NO other operation on u or v in between.
    
    # Function to get next op on qubits
    def get_next_ops_on(ops, start_idx, qubits):
        # Return list of (index, op) for the next operation on each qubit in `qubits`
        # `qubits` is a set of qubit indices.
        next_ops = {}
        for i in range(start_idx, len(ops)):
            op_name, *op_args = ops[i]
            # Check if op involves any of the qubits
            # args are qubit indices for single/two qubit gates
            involved = set()
            if op_name == "CX":
                involved = {op_args[0], op_args[1]}
            else:
                involved = {op_args[0]}
            
            for q in involved:
                if q in qubits and q not in next_ops:
                    next_ops[q] = (i, ops[i])
            
            if all(q in next_ops for q in qubits):
                break
        return next_ops

    # This is O(N^2) or worse.
    # Better: build dependency chains for each qubit.
    # qubit_ops = {q: [list of (op_index, op_data)]}
    
    qubit_chains = collections.defaultdict(list)
    for idx, op in enumerate(flat_ops):
        op_name, *args = op
        if op_name == "CX":
            u, v = args
            qubit_chains[u].append(idx)
            qubit_chains[v].append(idx)
        else:
            u = args[0]
            qubit_chains[u].append(idx)
            
    # Now iterate and mark ops to skip (part of SWAP)
    skip_indices = set()
    swaps_found = [] # (index, u, v)
    
    for idx, op in enumerate(flat_ops):
        if idx in skip_indices:
            continue
        
        if op[0] == "CX":
            u, v = op[1], op[2]
            
            # Check if this is start of SWAP(u, v)
            # Pattern 1: CX u v, CX v u, CX u v
            # Pattern 2: CX v u, CX u v, CX v u
            
            # Find next op on u and v
            # Using qubit_chains
            # current op is at idx.
            # u's chain: ... idx, next_u, ...
            # v's chain: ... idx, next_v, ...
            
            try:
                u_pos_in_chain = qubit_chains[u].index(idx)
                v_pos_in_chain = qubit_chains[v].index(idx)
                
                if u_pos_in_chain + 1 >= len(qubit_chains[u]) or v_pos_in_chain + 1 >= len(qubit_chains[v]):
                    continue
                    
                idx2_u = qubit_chains[u][u_pos_in_chain + 1]
                idx2_v = qubit_chains[v][v_pos_in_chain + 1]
                
                if idx2_u != idx2_v:
                    continue # Next ops on u and v are different -> not a 2-qubit gate on (u,v)
                
                idx2 = idx2_u
                op2 = flat_ops[idx2]
                
                if op2[0] != "CX":
                    continue
                
                # Check pattern
                # Op1: CX u v
                # Op2 should be CX v u
                if op2[1] == v and op2[2] == u:
                    # Good. Check Op3.
                    if u_pos_in_chain + 2 >= len(qubit_chains[u]) or v_pos_in_chain + 2 >= len(qubit_chains[v]):
                        continue
                    
                    idx3_u = qubit_chains[u][u_pos_in_chain + 2]
                    idx3_v = qubit_chains[v][v_pos_in_chain + 2]
                    
                    if idx3_u != idx3_v:
                        continue
                    
                    idx3 = idx3_u
                    op3 = flat_ops[idx3]
                    
                    if op3[0] == "CX" and op3[1] == u and op3[2] == v:
                        # FOUND SWAP!
                        print(f"Found SWAP at {idx}, {idx2}, {idx3} on {u}, {v}")
                        skip_indices.add(idx)
                        skip_indices.add(idx2)
                        skip_indices.add(idx3)
                        swaps_found.append((idx, u, v))
                        
            except ValueError:
                continue

    print(f"Total SWAPs found: {len(swaps_found)}")
    
    # Rebuild circuit with tracking
    new_ops = []
    # We need to process ops in original order, but with mapping.
    # And handle the identified SWAPs.
    
    current_map = {i: i for i in range(circuit.num_qubits)} # Logical code wire -> Physical wire
    
    # We iterate 0 to len(flat_ops).
    # If idx is in skip_indices, check if it is the START of a swap.
    # If so, update map.
    # Else, continue.
    
    swap_starts = {s[0]: (s[1], s[2]) for s in swaps_found}
    
    for idx, op in enumerate(flat_ops):
        if idx in skip_indices:
            if idx in swap_starts:
                u, v = swap_starts[idx]
                # Update map: swap locations of logical u and v?
                # Wait. The SWAP in code is `SWAP u v`.
                # It means: state at u moves to v, state at v moves to u.
                # My `current_map` says: logical wire `w` is at physical wire `p`.
                # `current_map[u]` is the physical location of logical `u`.
                # `current_map[v]` is the physical location of logical `v`.
                # After SWAP, logical `u` should be at `old_map[v]`.
                # logical `v` should be at `old_map[u]`.
                
                p_u = current_map[u]
                p_v = current_map[v]
                
                current_map[u] = p_v
                current_map[v] = p_u
            continue
            
        # Normal op
        op_name, *args = op
        # Map args
        new_args = [current_map[a] for a in args]
        
        # Add to new ops
        new_ops.append((op_name, *new_args))
        
    # Build final circuit
    final_circ = stim.Circuit()
    for op in new_ops:
        name = op[0]
        targets = op[1:]
        final_circ.append(name, targets)
        
    # Check final permutation
    # `current_map` maps logical -> physical
    # If `current_map[i] != i`, we have a permutation.
    # We need to restore it.
    # logical `i` is at `current_map[i]`. We want it at `i`.
    
    # Calculate inverse permutation: physical -> logical
    # We want physical `p` to hold logical `p`.
    # Currently physical `p` holds logical `current_map^-1[p]`.
    
    perm = []
    for i in range(circuit.num_qubits):
        # We want to know which logical qubit is at physical location i.
        # Find k such that current_map[k] == i.
        k = -1
        for log_q, phys_q in current_map.items():
            if phys_q == i:
                k = log_q
                break
        perm.append(k)
    
    print(f"Final permutation (phys i holds logical perm[i]): {perm}")
    
    # Check if permutation is identity
    is_identity = all(perm[i] == i for i in range(len(perm)))
    
    if is_identity:
        print("Final permutation is identity! No fixup needed.")
    else:
        print("Final permutation is NOT identity. Calculating fixup cost.")
        # We need to sort `perm` to identity using SWAPs.
        # Count cycles.
        visited = [False] * len(perm)
        swaps_needed = 0
        for i in range(len(perm)):
            if not visited[i]:
                cycle_len = 0
                curr = i
                while not visited[curr]:
                    visited[curr] = True
                    curr = perm[curr] # Move to where the element at curr should go? 
                    # Wait, perm[i] is the logical qubit at physical i.
                    # We want logical i at physical i.
                    # This is equivalent to sorting the array `perm` to `0, 1, 2...` by swapping elements.
                    cycle_len += 1
                if cycle_len > 1:
                    swaps_needed += (cycle_len - 1)
                    
        print(f"Swaps needed to restore: {swaps_needed}")
        cx_cost_fixup = swaps_needed * 3
        print(f"CX cost of fixup: {cx_cost_fixup}")
        
        saved_swaps = len(swaps_found)
        saved_cx = saved_swaps * 3
        print(f"CX saved by removal: {saved_cx}")
        
        net_gain = saved_cx - cx_cost_fixup
        print(f"Net CX gain: {net_gain}")
        
        if net_gain > 0:
            print("Improvement found!")
            # Add SWAPs to `final_circ` to fix permutation
            # We can do this by appending SWAP gates corresponding to the swaps needed to sort.
            
            # To implement the sort:
            # We have logical qubits at physical locations. `perm[p]` = logical qubit at p.
            # We want `perm[p] == p`.
            # We can iterate and swap.
            
            # Make a mutable copy of perm to track swaps
            curr_perm = list(perm)
            # Map logical -> physical location (inverse of curr_perm)
            # log_loc[l] = p  means logical l is at physical p.
            log_loc = {l: p for p, l in enumerate(curr_perm)}
            
            fixup_swaps = []
            
            for i in range(len(curr_perm)):
                if curr_perm[i] != i:
                    # We want logical i to be at physical i.
                    # Currently logical i is at `log_loc[i]`.
                    # The element at physical i is `curr_perm[i]` (let's call it X).
                    
                    pos_of_i = log_loc[i]
                    # We want to swap physical i and physical pos_of_i.
                    
                    # Record swap
                    fixup_swaps.append((i, pos_of_i))
                    final_circ.append("SWAP", [i, pos_of_i])
                    
                    # Update state
                    val_at_i = curr_perm[i] # X
                    # Swap in curr_perm
                    curr_perm[i], curr_perm[pos_of_i] = curr_perm[pos_of_i], curr_perm[i]
                    
                    # Update inverse map
                    log_loc[val_at_i] = pos_of_i
                    log_loc[i] = i
                    
            print(f"Added {len(fixup_swaps)} SWAPs for fixup.")
            
    # Save optimized circuit
    with open("data/agent_files/candidate_optimized.stim", "w") as f:
        f.write(str(final_circ))
        
    print(f"Original CX: {count_cx(circuit)}")
    print(f"New CX: {count_cx(final_circ)}")
    
def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
        elif instruction.name == "SWAP":
            count += 3 * (len(instruction.targets_copy()) // 2)
    return count

if __name__ == "__main__":
    main()
