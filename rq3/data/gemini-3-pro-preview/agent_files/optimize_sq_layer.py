import stim
import itertools

def get_single_qubit_gates():
    # List of primitive single qubit gates with cost 1
    # We include X, Y, Z, H, S, S_DAG, SQRT_X, SQRT_X_DAG, SQRT_Y, SQRT_Y_DAG
    # C_XYZ might be supported but let's stick to standard ones first.
    # Actually, let's include all standard stim single qubit gates.
    gates = [
        "I", "X", "Y", "Z", 
        "H", 
        "S", "S_DAG", 
        "SQRT_X", "SQRT_X_DAG", 
        "SQRT_Y", "SQRT_Y_DAG"
    ]
    # We want to find the shortest sequence for each Clifford.
    # There are 24 single qubit Cliffords.
    return gates

def get_gate_tableau(gate_name):
    return stim.Tableau.from_circuit(stim.Circuit(f"{gate_name} 0"))

def generate_clifford_table():
    gates = get_single_qubit_gates()
    gate_tableaus = {g: get_gate_tableau(g) for g in gates if g != "I"}
    
    # Map tableau string to shortest gate sequence
    table = {}
    
    # BFS to find shortest sequences
    queue = [([], stim.Tableau(1))]
    visited = set()
    visited.add(str(stim.Tableau(1)))
    table[str(stim.Tableau(1))] = []
    
    # We limit depth to 3-4 as any Clifford can be done in small number of steps
    for depth in range(1, 5):
        new_queue = []
        for seq, tab in queue:
            for g, g_tab in gate_tableaus.items():
                
                new_seq = seq + [g]
                
                # Apply gate
                new_tab = tab.copy()
                new_tab.append(g_tab, [0])
                
                s = str(new_tab)
                if s not in visited:
                    visited.add(s)
                    table[s] = new_seq
                    new_queue.append((new_seq, new_tab))
                    
        queue = new_queue
        if len(visited) >= 24:
            break
            
    return table

def optimize_circuit(input_file, output_file):
    c = stim.Circuit.from_file(input_file)
    
    # Split into part before final SQ layer and final SQ layer
    # We know the structure is H layer, CZ layer, then SQ layer.
    # But CZ layer might be interleaved?
    # Actually, graph state form is H then CZ then SQ.
    # Let's just process the whole circuit by tracking individual qubits?
    # But we want to preserve the CZ structure (since CX=0).
    # So we only optimize the 1-qubit gates that come AFTER the last 2-qubit gate on that qubit.
    
    # However, simpler approach:
    # 1. Identify the cut point where CZs end.
    # 2. Slice the circuit.
    
    # Let's look at the candidate.stim structure again.
    # Line 2 is CZ ...
    # Line 3+ are SQ gates.
    # So we can just take everything after the CZ block.
    
    # We'll assume the file format from candidate.stim
    # We will rebuild the circuit.
    
    final_circuit = stim.Circuit()
    
    # We need to track the state of each qubit after the CZ layer
    # But wait, we can just grab the tail of the circuit.
    
    # Let's iterate through instructions.
    # If it's a 2-qubit gate (CZ), append to final_circuit.
    # If it's a 1-qubit gate, buffer it per qubit.
    # But we need to know when 'final' layer starts.
    # In the candidate, CZ are all in one block.
    
    # Let's do this:
    # 1. Keep all instructions up to the last 2-qubit gate.
    # 2. For the remaining 1-qubit gates, collapse them into a tableau per qubit.
    # 3. Replace with optimal sequence.
    
    # Find the index of the last 2-qubit gate
    last_2q_idx = -1
    for i, inst in enumerate(c):
        if len(inst.targets_copy()) > 1: # This check is approximate, CZ has 2 targets per pair?
             # stim instructions like CZ 0 1 2 3 are one instruction with multiple targets.
             # targets are pairs.
             # Any gate with >1 target or name like CZ, CX, etc.
             if inst.name in ["CX", "CY", "CZ", "ISWAP", "SWAP"]: # Add others if needed
                 last_2q_idx = i
    
    # Rebuild
    head = stim.Circuit()
    tail_ops = [[] for _ in range(c.num_qubits)]
    
    for i, inst in enumerate(c):
        if i <= last_2q_idx:
            head.append(inst)
        else:
            # It's a 1-qubit gate (or multiple 1-qubit gates in one line)
            name = inst.name
            for t in inst.targets_copy():
                tail_ops[t.value].append(name)

    # Now optimize tails
    clifford_table = generate_clifford_table()
    
    tail_circuit = stim.Circuit()
    
    # We group by gate name
    from collections import defaultdict
    
    # Reset
    qubit_sequences = {} # q -> list of ops
    
    for q in range(c.num_qubits):
        ops = tail_ops[q]
        if not ops:
            continue
            
        # Compute unitary
        t = stim.Tableau(1)
        for op in ops:
            t.append(stim.Tableau.from_circuit(stim.Circuit(f"{op} 0")), [0])
            
        # Find optimal
        s = str(t)
        if s in clifford_table:
            best_seq = clifford_table[s]
            qubit_sequences[q] = best_seq
        else:
            # Should not happen if table is complete (24 cliffords)
            print(f"Warning: Clifford not found for qubit {q}")
            # Fallback: keep original? Or synthesized?
            # If not found, we just append the original ops (which is safe but suboptimal)
            qubit_sequences[q] = ops

    # Determine max sequence length
    max_seq_len = 0
    if qubit_sequences:
        max_seq_len = max(len(seq) for seq in qubit_sequences.values())
        
    for k in range(max_seq_len):
        # Find all (op, q) for this k
        layer_ops = defaultdict(list)
        for q, seq in qubit_sequences.items():
            if k < len(seq):
                op = seq[k]
                layer_ops[op].append(q)
        
        # Append this layer to circuit
        for op, qubits in layer_ops.items():
            tail_circuit.append(op, qubits)
        
    final_circuit += tail_circuit
    
    with open(output_file, "w") as f:
        f.write(str(final_circuit))

if __name__ == "__main__":
    optimize_circuit("candidate.stim", "candidate_opt.stim")
