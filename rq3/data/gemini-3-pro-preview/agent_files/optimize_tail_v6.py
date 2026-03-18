import stim
import collections
import heapq

def get_clifford_map_weighted():
    gates = ["H", "S", "S_DAG", "X", "Y", "Z"]
    
    weights = {
        "H": 100, "X": 100, "Y": 100,
        "S": 1, "S_DAG": 1, "Z": 1
    }
    
    # Precompute gate tableaus
    gate_tabs = {}
    for g in gates:
        gate_tabs[g] = stim.Tableau.from_circuit(stim.Circuit(f"{g} 0"))
        
    start_tab = stim.Tableau(1)
    
    # (cost, counter, seq, tableau)
    pq = []
    heapq.heappush(pq, (0, 0, [], start_tab))
    
    visited_cost = {} 
    final_map = {}
    counter = 0
    
    while pq:
        cost, _, seq, tab = heapq.heappop(pq)
        
        key = str(tab)
        
        if key in visited_cost and visited_cost[key] <= cost:
            continue
        visited_cost[key] = cost
        
        if key not in final_map:
            final_map[key] = seq
            
        if len(final_map) >= 24:
            break
            
        if len(seq) >= 5: 
            continue
            
        for g in gates:
            counter += 1
            new_cost = cost + weights[g]
            new_seq = seq + [g]
            
            t_new = tab.copy()
            # Append gate tableau
            t_new.append(gate_tabs[g], [0])
            
            heapq.heappush(pq, (new_cost, counter, new_seq, t_new))
            
    return final_map

def optimize_tail(input_path, output_path):
    with open(input_path, "r") as f:
        c = stim.Circuit(f.read())
        
    split_idx = -1
    for i, instr in enumerate(c):
        if len(instr.targets_copy()) > 1: 
            if instr.name in ["CZ", "CX", "CY", "CNOT", "SWAP", "ISWAP"]:
                split_idx = i
                
    head = c[:split_idx+1]
    tail = c[split_idx+1:]
    
    num_qubits = c.num_qubits
    qubit_ops = collections.defaultdict(list)
    
    for instr in tail:
        if instr.name == "TICK":
            continue
        for t in instr.targets_copy():
            if t.is_qubit_target:
                qubit_ops[t.value].append(instr.name)
                
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
    try:
        optimize_tail("candidate.stim", "candidate_opt_weighted.stim")
        print("Optimization complete.")
    except Exception as e:
        print(f"Error: {e}")
