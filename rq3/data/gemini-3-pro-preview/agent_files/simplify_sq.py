import stim
import collections

def get_optimal_sequences():
    gates = [
        ('X', stim.Tableau.from_circuit(stim.Circuit('X 0'))),
        ('Y', stim.Tableau.from_circuit(stim.Circuit('Y 0'))),
        ('Z', stim.Tableau.from_circuit(stim.Circuit('Z 0'))),
        ('H', stim.Tableau.from_circuit(stim.Circuit('H 0'))),
        ('S', stim.Tableau.from_circuit(stim.Circuit('S 0'))),
        ('S_DAG', stim.Tableau.from_circuit(stim.Circuit('S_DAG 0'))),
        ('SQRT_X', stim.Tableau.from_circuit(stim.Circuit('SQRT_X 0'))),
        ('SQRT_X_DAG', stim.Tableau.from_circuit(stim.Circuit('SQRT_X_DAG 0'))),
        ('SQRT_Y', stim.Tableau.from_circuit(stim.Circuit('SQRT_Y 0'))),
        ('SQRT_Y_DAG', stim.Tableau.from_circuit(stim.Circuit('SQRT_Y_DAG 0'))),
    ]
    
    queue = collections.deque([([], stim.Tableau(1))])
    visited = {str(stim.Tableau(1)): []}
    
    while queue:
        seq, tab = queue.popleft()
        
        if len(seq) >= 3: 
            continue
            
        for name, g_tab in gates:
            new_tab = tab.then(g_tab)
            if str(new_tab) not in visited:
                new_seq = seq + [name]
                visited[str(new_tab)] = new_seq
                queue.append((new_seq, new_tab))
                
    return visited

def solve():
    try:
        with open('candidate.stim', 'r') as f:
            text = f.read()
            c = stim.Circuit(text)
    except:
        print('candidate.stim not found')
        return

    last_two_qubit_idx = -1
    for i, op in enumerate(c):
        if op.name in ['CX', 'CZ', 'CY', 'CNOT', 'XCZ', 'XCY', 'XCX'] or len(op.targets_copy()) > 1:
            last_two_qubit_idx = i
            
    if last_two_qubit_idx == -1:
        # No 2-qubit gates, treat whole as tail
        head = stim.Circuit()
        tail = c
    else:
        head = c[:last_two_qubit_idx+1]
        tail = c[last_two_qubit_idx+1:]
    
    # Generate optimal sequences mapping
    optimal_seqs = get_optimal_sequences()
    num_qubits = c.num_qubits
    
    new_tail_ops = [[] for _ in range(num_qubits)]
    
    for q in range(num_qubits):
        q_tail = stim.Circuit()
        for op in tail:
            for t in op.targets_copy():
                if t.value == q:
                    # Remap to qubit 0
                    q_tail.append(op.name, [0])
        
        if len(q_tail) == 0:
            continue

        q_tab = stim.Tableau.from_circuit(q_tail)
        
        if str(q_tab) in optimal_seqs:
            seq = optimal_seqs[str(q_tab)]
            new_tail_ops[q] = seq
        else:
            # Fallback if not found in depth 3 search
            # Just keep original operations for this qubit
            new_tail_ops[q] = [op.name for op in q_tail]

    final_tail = stim.Circuit()
    for q in range(num_qubits):
        for op_name in new_tail_ops[q]:
            final_tail.append(op_name, [q])
            
    final = head + final_tail
    
    with open('candidate_final.stim', 'w') as f:
        f.write(str(final))
    print('Optimized final candidate generated.')

if __name__ == '__main__':
    solve()
