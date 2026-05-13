import sys

# The baseline circuit provided in the prompt
BASELINE_CIRCUIT = """H 0
S 21 31
H 4 5 8 18 19 22
CX 0 4 0 5 0 8 0 18 0 19 0 21 0 22 0 31 0 32
H 14 28 29
CX 14 0 28 0 29 0 31 1 1 31 31 1
H 1
S 1
CX 1 32
S 7
H 4 5 7 8 14 18 19 22 32
CX 4 1 5 1 7 1 8 1 14 1 18 1 19 1 22 1 28 1 29 1 32 1 7 2 2 7 7 2
H 2
S 2
H 14
CX 14 2 28 2 29 2 21 3 3 21 21 3
S 3
H 3
S 3 14
CX 3 14 28 3 29 3 14 4 4 14 14 4
S 4
H 4
CX 28 4 29 4 31 5 5 31 31 5
H 5 32
CX 5 22 5 32
H 15
CX 15 5 28 5 8 6 6 8 8 6
H 6 8 10 13 21 22 30 34
CX 6 8 6 10 6 13 6 15 6 21 6 22 6 28 6 30 6 32 6 34 22 6 28 6 28 7 7 28 28 7
H 22
CX 7 8 7 10 7 13 7 21 7 22 7 30 7 32 7 34 15 7 15 8 8 15 15 8
H 8
CX 8 32
H 32
CX 22 8 32 8 22 9 9 22 22 9 32 9 28 10 10 28 28 10
H 10
S 23
H 14 17 18 22 33 34
CX 10 14 10 17 10 18 10 21 10 22 10 23 10 32 10 33 10 34
H 16
CX 16 10 29 10 22 11 11 22 22 11
H 32
CX 11 32
S 23
H 23
CX 23 11 29 11 16 12 12 16 16 12
S 32
H 23
CX 12 14 12 17 12 18 12 21 12 23 12 32 12 33 12 34 29 12 23 13 13 23 23 13
H 13
CX 13 14 13 17 13 18 13 21 13 32 13 33 13 34 29 13 32 14 14 32 32 14
H 14
S 14
H 17 18 21 32 33 34
CX 17 14 18 14 21 14 29 14 32 14 33 14 34 14 17 15 15 17 17 15
H 15
CX 15 24 15 33 15 34
H 21
CX 21 15 30 15 24 16 16 24 24 16
H 16 21 34
CX 16 21 16 33 16 34 28 16 30 16 21 17 17 21 21 17
H 28
CX 17 28 17 33
H 33 34
CX 30 17 33 17 34 17 34 18 18 34 34 18
H 18 33
CX 18 28 18 33
H 28 33
CX 28 18 30 18 33 18 28 19 19 28 28 19
H 33
CX 19 33 30 19 29 20 20 29 29 20
H 22 32 34
CX 20 21 20 22 20 23 20 25 20 32 20 33 20 34 30 20 32 20 34 20 25 21 21 25 25 21
H 21 32
CX 21 32 21 33 22 21 30 21 32 22 22 32 32 22
H 32
CX 22 32 22 33
H 33
CX 30 22 33 22 34 22 34 23 23 34 34 23
H 23 33
CX 23 32 23 33
H 32
CX 30 23 32 23 32 24 24 32 32 24 30 24 28 25 25 28 28 25
H 25 31 32
CX 25 26 25 28 25 30 25 31 25 32 25 33 25 34 30 25 31 25
H 26 31
CX 26 31 26 33 30 26 32 26 31 27 27 31 31 27
H 32
CX 27 32 27 33
H 33
CX 30 27 33 27 32 28 28 32 32 28
S 28
H 28
S 28
H 33
CX 28 33
S 30
H 30 32 33 34
CX 30 28 32 28 33 28 34 28 30 29 29 30 30 29
H 29
S 29
H 32 33 34
CX 29 32 29 33 29 34
H 33
CX 33 29
H 30 33
CX 30 31 30 33 32 30
H 31
S 31 32 33
CX 31 32 31 33 34 31 33 32 32 33 33 32
H 32
S 32
H 33 34
CX 32 33 32 34
H 33
S 33
CX 33 34
H 34 1 3 9 11 13 17 22 27 32
S 1 1 3 3 9 9 11 11 13 13 17 17 22 22 27 27 32 32
H 1 3 9 11 13 17 22 27 32
S 0 0 2 2 3 3 4 4 6 6 7 7 10 10 14 14 15 15 17 17 20 20 22 22 25 25 27 27 29 29 30 30 32 32 33 33 34 34"""

def parse_circuit(circuit_str):
    ops = []
    lines = circuit_str.strip().split('\n')
    for line in lines:
        if '#' in line: line = line.split('#')[0]
        if not line.strip(): continue
        parts = line.strip().split()
        gate = parts[0]
        qubits = [int(x) for x in parts[1:]]
        
        if gate in ['CX', 'CNOT']:
            for i in range(0, len(qubits), 2):
                ops.append({'gate': 'CX', 'qubits': [qubits[i], qubits[i+1]]})
        elif gate in ['H', 'S', 'X', 'Y', 'Z', 'I', 'M']:
            for q in qubits:
                ops.append({'gate': gate, 'qubits': [q]})
        else:
             # Assume single qubit gate or handle appropriately
            for q in qubits:
                 ops.append({'gate': gate, 'qubits': [q]})
    return ops

def main():
    ops = parse_circuit(BASELINE_CIRCUIT)
    
    # Analyze circuit to find long runs of same control
    # We will insert flag checks.
    
    # We need to allocate new flag qubits.
    # We assign one flag per data qubit 0..34
    # Flag for qubit i is 35 + i.
    # Total ancillas = 35 (indices 35..69).
    
    THRESHOLD = 1 # If >= 1 targets, wrap. To catch all high-degree nodes even if interleaved.
    
    # Pre-calculate flags
    flags = {} # qubit -> flag_index
    next_flag = 35
    
    def get_flag(q):
        nonlocal next_flag
        if q not in flags:
            flags[q] = next_flag
            next_flag += 1
        return flags[q]

    insertions = [] # list of (index, op_str, type)
    
    # Track runs
    # For each qubit, we track current run of CXs where it is control OR target.
    # run = {'start_idx': i, 'count': n, 'last_idx': i, 'mode': 'control'|'target'}
    current_runs = {} # qubit -> run_info
    
    # Also track "active" qubits to prevent premature closing if idle
    # But idle is fine.
    
    for i, op in enumerate(ops):
        gate = op['gate']
        qubits = op['qubits']
        
        touched = set(qubits)
        
        control = None
        target = None # Single target for CX
        if gate == 'CX':
            control = qubits[0]
            target = qubits[1]
        
        # Check interruptions
        # Any qubit touched by this op must be checked.
        # If it matches current mode, continue. Else break.
        
        # We iterate over touched qubits to update/start runs.
        # But we also need to close runs for qubits NOT touched? No, idle is fine.
        # But wait. If a qubit is in a run, and we have an op that does NOT touch it.
        # The run continues (gap).
        # We only close when touched by incompatible op.
        
        # So check all active runs.
        keys_to_check = list(current_runs.keys())
        for q in keys_to_check:
            if q not in touched:
                continue # Idle, continue run
            
            run = current_runs[q]
            mode = run['mode']
            
            compatible = False
            if mode == 'control':
                if q == control: compatible = True
            elif mode == 'target':
                if q == target: compatible = True
            
            if not compatible:
                # Interrupted! Close run.
                if run['count'] >= THRESHOLD:
                    f = get_flag(q)
                    if mode == 'control':
                        # X-check
                        insertions.append({'idx': run['start_idx'], 'op': f"CX {q} {f}", 'pos': 'before'})
                        insertions.append({'idx': run['last_idx'] + 1, 'op': f"CX {q} {f}", 'pos': 'after'})
                    else:
                        # Z-check
                        # H f, CX f q ... CX f q, H f
                        # We need multiple ops.
                        insertions.append({'idx': run['start_idx'], 'op': f"H {f}", 'pos': 'before'})
                        insertions.append({'idx': run['start_idx'], 'op': f"CX {f} {q}", 'pos': 'before'})
                        
                        insertions.append({'idx': run['last_idx'] + 1, 'op': f"CX {f} {q}", 'pos': 'after'})
                        insertions.append({'idx': run['last_idx'] + 1, 'op': f"H {f}", 'pos': 'after'})
                del current_runs[q]
        
        # Now start/update runs for touched qubits
        if gate == 'CX':
            # Control
            c = control
            if c in current_runs:
                # Must be compatible (checked above).
                current_runs[c]['count'] += 1
                current_runs[c]['last_idx'] = i
            else:
                current_runs[c] = {'start_idx': i, 'count': 1, 'last_idx': i, 'mode': 'control'}
            
            # Target
            t = target
            if t in current_runs:
                current_runs[t]['count'] += 1
                current_runs[t]['last_idx'] = i
            else:
                current_runs[t] = {'start_idx': i, 'count': 1, 'last_idx': i, 'mode': 'target'}
        else:
            # Non-CX gate. Already closed above (since incompatible with everything).
            pass

    # Close any remaining runs
    for q, run in current_runs.items():
        if run['count'] >= THRESHOLD:
            f = get_flag(q)
            mode = run['mode']
            if mode == 'control':
                insertions.append({'idx': run['start_idx'], 'op': f"CX {q} {f}", 'pos': 'before'})
                insertions.append({'idx': run['last_idx'] + 1, 'op': f"CX {q} {f}", 'pos': 'after'})
            else:
                insertions.append({'idx': run['start_idx'], 'op': f"H {f}", 'pos': 'before'})
                insertions.append({'idx': run['start_idx'], 'op': f"CX {f} {q}", 'pos': 'before'})
                insertions.append({'idx': run['last_idx'] + 1, 'op': f"CX {f} {q}", 'pos': 'after'})
                insertions.append({'idx': run['last_idx'] + 1, 'op': f"H {f}", 'pos': 'after'})


    # Sort insertions
    # Sort by index primarily.
    # If inserting multiple at same index?
    # e.g. at index 5.
    # To be safe, just use stable sort.
    
    insertions.sort(key=lambda x: x['idx'])
    
    # Construct new ops
    final_ops = []
    
    # Process original ops one by one, inserting as needed.
    # Note: insertions with 'idx' k are inserted before or after op[k] logic?
    # My logic: 'before' at start_idx -> before op[start_idx].
    # 'after' at last_idx+1 -> before op[last_idx+1].
    # So effectively all insertions are "before op[idx]".
    # Yes.
    
    curr_ins = 0
    
    for i in range(len(ops) + 1):
        # Insert all scheduled for this index
        while curr_ins < len(insertions) and insertions[curr_ins]['idx'] == i:
            final_ops.append(insertions[curr_ins]['op'])
            curr_ins += 1
        
        if i < len(ops):
            op = ops[i]
            q_str = " ".join(map(str, op['qubits']))
            final_ops.append(f"{op['gate']} {q_str}")

    print("\n".join(final_ops))
    
    ancilla_list = sorted(list(flags.values()))
    # Print ancillas as comment line
    print(f"# ANCILLAS: {ancilla_list}")

if __name__ == "__main__":
    main()
