import stim
import collections
import heapq

def get_clifford_map_weighted():
    # Dijkstra to find best sequence for each of the 24 single qubit Cliffords
    # Cost: H, X, Y = 100. S, S_DAG, Z = 1.
    # This prioritizes avoiding H/X/Y, then shortest length.
    
    # Gates
    gates = ["H", "S", "S_DAG", "X", "Y", "Z"]
    
    # Weights
    weights = {
        "H": 100, "X": 100, "Y": 100,
        "S": 1, "S_DAG": 1, "Z": 1
    }
    
    # Map from string(Tableau) -> list of gate names
    found = {}
    
    # Priority Queue: (cost, seq, tableau)
    # tableau cannot be in PQ directly if not comparable. Use string key for visited check.
    # But we need the tableau object to extend.
    # We can store (cost, seq) and reconstruct tableau or store tableau wrapper.
    # Or just use `id(tableau)`? No.
    # We'll just recompute tableau from seq? No, too slow.
    # Store `str(tableau)` in visited set.
    
    start_tab = stim.Tableau(1)
    start_key = str(start_tab)
    
    pq = [(0, [], start_tab)]
    
    visited_cost = {} # Key -> cost
    
    final_map = {}
    
    while pq:
        cost, seq, tab = heapq.heappop(pq)
        
        key = str(tab)
        
        # If we found this tableau with lower cost before, skip
        if key in visited_cost and visited_cost[key] <= cost:
            continue
        visited_cost[key] = cost
        
        # If this is the first time we pop this key, it's the optimal path (Dijkstra property)
        if key not in final_map:
            final_map[key] = seq
            
        # If we have all 24, can we stop?
        # Only if we are sure we won't find a better path to an already found one?
        # Dijkstra guarantees that when we pop, it's the best path to that node.
        # So yes, if len(final_map) == 24, we are done.
        if len(final_map) >= 24:
            break
            
        # Pruning
        if len(seq) >= 5: # Max depth safety
            continue
            
        for g in gates:
            new_cost = cost + weights[g]
            new_seq = seq + [g]
            
            # Compute new tableau
            # Efficiently: copy and append?
            # t_new = tab.copy()
            # t_new.append(stim.Circuit(f"{g} 0"), [0])
            # But tab.copy() might be slow? It's fine for small depth.
            t_new = tab.copy()
            # Fix: use proper append
            t_new.append(stim.CircuitInstruction(g, [0]))
            
            heapq.heappush(pq, (new_cost, new_seq, t_new))
            
    return final_map

def optimize_tail(input_path, output_path):
    with open(input_path, "r") as f:
        c = stim.Circuit(f.read())
        
    # Split
    split_idx = -1
    for i, instr in enumerate(c):
        if len(instr.targets_copy()) > 1: 
            if instr.name in ["CZ", "CX", "CY", "CNOT", "SWAP", "ISWAP"]:
                split_idx = i
    
    head = c[:split_idx+1]
    tail = c[split_idx+1:]
    
    # Group by qubit
    num_qubits = c.num_qubits
    qubit_ops = collections.defaultdict(list)
    
    for instr in tail:
        if instr.name == "TICK":
            continue
        for t in instr.targets_copy():
            if t.is_qubit_target:
                qubit_ops[t.value].append(instr.name)
                
    # Optimize
    clifford_map = get_clifford_map_weighted()
    optimized_ops = {}
    max_len = 0
    
    for q in range(num_qubits):
        ops = qubit_ops[q]
        if not ops:
            optimized_ops[q] = []
            continue
            
        c_temp = stim.Circuit()
        for op in ops:
            c_temp.append(op, [0])
        t_q = stim.Tableau.from_circuit(c_temp)
        
        key = str(t_q)
        if key in clifford_map:
            best = clifford_map[key]
            optimized_ops[q] = best
            max_len = max(max_len, len(best))
        else:
            optimized_ops[q] = ops
            max_len = max(max_len, len(ops))

    # Reconstruct
    new_tail = stim.Circuit()
    for d in range(max_len):
        layer_gates = collections.defaultdict(list)
        for q in range(num_qubits):
            seq = optimized_ops[q]
            if d < len(seq):
                op = seq[d]
                layer_gates[op].append(q)
        
        for op, targets in layer_gates.items():
            new_tail.append(op, targets)
            
    final = head + new_tail
    
    with open(output_path, "w") as f:
        f.write(str(final))

if __name__ == "__main__":
    optimize_tail("candidate.stim", "candidate_opt_weighted.stim")
