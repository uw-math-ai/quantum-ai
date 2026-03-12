import stim
import collections

def generate_cliffords():
    # 24 single qubit cliffords
    # Use BFS
    gates = ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]
    
    start_tableau = stim.Tableau(1)
    start_key = str(start_tableau)
    queue = collections.deque([(start_tableau, [])])
    seen = {start_key: []}
    
    while queue:
        tab, seq = queue.popleft()
        
        if len(seq) >= 4:
            continue
            
        gates = ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]
        for gate in gates:
            if gate == "I": continue
            
            gate_tab = stim.Tableau.from_named_gate(gate)
            new_tab = tab.then(gate_tab)
            
            key = str(new_tab)
            if key not in seen:
                seen[key] = seq + [gate]
                queue.append((new_tab, seq + [gate]))
                
            if len(seen) == 24:
                return seen
    return seen

def run_optimization():
    clifford_map = generate_cliffords()
    print(f"Found {len(clifford_map)} Cliffords")

    with open("candidate_graph_v2.stim", "r") as f:
        content = f.read()

    lines = content.strip().splitlines()
    header_lines = []
    tail_lines = []
    
    for i, line in enumerate(lines):
        if line.startswith("H ") or line.startswith("CZ "):
            header_lines.append(line)
        else:
            tail_lines = lines[i:]
            break
            
    header_circuit = stim.Circuit("\n".join(header_lines))
    tail_circuit = stim.Circuit("\n".join(tail_lines))
    
    final_circuit = header_circuit.copy()
    
    for q in range(35):
        q_ops = []
        for instr in tail_circuit:
            for t in instr.targets_copy():
                if t.value == q:
                    q_ops.append(instr.name)
        
        q_tab = stim.Tableau(1)
        for op in q_ops:
            gate_tab = stim.Tableau.from_named_gate(op)
            q_tab = q_tab.then(gate_tab)
            
        key = str(q_tab)
        best_seq = clifford_map.get(key)
        
        if best_seq is None:
            # Fallback
            for op in q_ops:
                final_circuit.append(op, [q])
        else:
            for op in best_seq:
                final_circuit.append(op, [q])
                
    print(final_circuit)

if __name__ == "__main__":
    run_optimization()

