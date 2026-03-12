import stim
from collections import deque

def get_single_qubit_gates():
    return ["I", "X", "Y", "Z", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]

def get_gate_tableau(gate_name):
    return stim.Tableau.from_circuit(stim.Circuit(f"{gate_name} 0"))

def generate_clifford_table():
    gates = get_single_qubit_gates()
    # Map gate name to its tableau
    gate_tableaus = {g: get_gate_tableau(g) for g in gates if g != "I"}
    
    # Map tableau string to shortest gate sequence
    table = {}
    
    # BFS to find shortest sequences
    # Queue stores (sequence, tableau)
    initial_tab = stim.Tableau(1)
    queue = deque([([], initial_tab)])
    visited = set()
    
    initial_tab_str = str(initial_tab)
    visited.add(initial_tab_str)
    table[initial_tab_str] = []
    
    # There are 24 single qubit Cliffords.
    # We BFS up to depth 3 or 4 which should cover all.
    while len(table) < 24 and queue:
        seq, tab = queue.popleft()
        
        if len(seq) >= 3: 
            # If we reach depth 3, we might miss some (e.g. S H S H S) but 3 is usually enough.
            # Let's try to extend depth if needed.
            # Actually, standard generators H, S generate full group in short length.
            pass
            
        for g, g_tab in gate_tableaus.items():
            # Apply gate: new_tab = tab.then(g_tab) 
            # Stim's `then` applies the second tableau AFTER the first.
            new_tab = tab.then(g_tab)
            
            s = str(new_tab)
            if s not in visited:
                visited.add(s)
                new_seq = seq + [g]
                table[s] = new_seq
                queue.append((new_seq, new_tab))
                
    return table

def optimize_circuit(input_file, output_file):
    c = stim.Circuit.from_file(input_file)
    
    # Identify the last 2-qubit gate index
    last_2q_idx = -1
    for i, inst in enumerate(c):
        # We need to detect if instruction is multi-qubit.
        # CZ, CX, CY, etc.
        # Or simply if it involves >1 target.
        # But CZ 0 1 2 3 involves 2 targets per pair.
        # Let's check the gate name.
        if inst.name in ["CX", "CY", "CZ", "ISWAP", "SWAP", "CNOT", "XCX", "XCY", "XCZ", "YCX", "YCY", "YCZ"]: 
             last_2q_idx = i
    
    # Split into head (up to last 2q gate) and tail (single qubit gates after)
    head = stim.Circuit()
    tail_ops_per_qubit = [[] for _ in range(c.num_qubits)] # list of gate names
    
    for i, inst in enumerate(c):
        if i <= last_2q_idx:
            head.append(inst)
        else:
            # Add to respective qubits
            # Assuming 1-qubit gates only here
            for t in inst.targets_copy():
                if t.is_qubit_target:
                    tail_ops_per_qubit[t.value].append(inst.name)

    # Generate clifford table
    clifford_table = generate_clifford_table()
    
    # Reconstruct optimized tail
    optimized_tails = {}
    
    for q in range(c.num_qubits):
        ops = tail_ops_per_qubit[q]
        if not ops:
            optimized_tails[q] = []
            continue
            
        # Compute unitary for this qubit from sequence of ops
        t = stim.Tableau(1)
        for op_name in ops:
             op_tab = get_gate_tableau(op_name)
             t = t.then(op_tab)
             
        s = str(t)
        if s in clifford_table:
            optimized_tails[q] = clifford_table[s]
        else:
            print(f"Warning: Clifford not found for qubit {q}, using original.")
            optimized_tails[q] = ops

    # Determine max depth of optimized tails
    max_depth = 0
    if optimized_tails:
        max_depth = max(len(seq) for seq in optimized_tails.values())
        
    final_circuit = head.copy()
    
    # Append optimized tails layer by layer to keep parallelism
    for k in range(max_depth):
        gates_in_layer = {} # gate_name -> list of qubits
        for q, seq in optimized_tails.items():
            if k < len(seq):
                g = seq[k]
                if g not in gates_in_layer:
                    gates_in_layer[g] = []
                gates_in_layer[g].append(q)
                
        # Append gates for this layer
        # Sort gate names for stability
        for g in sorted(gates_in_layer.keys()):
            qubits = sorted(gates_in_layer[g])
            final_circuit.append(g, qubits)

    with open(output_file, "w") as f:
        f.write(str(final_circuit))

if __name__ == "__main__":
    optimize_circuit("candidate_graph_v3.stim", "candidate_opt_graph_v3.stim")
