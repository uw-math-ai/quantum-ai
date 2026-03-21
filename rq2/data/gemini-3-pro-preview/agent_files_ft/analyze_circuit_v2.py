
import re

circuit_str = "CX 13 0 0 13 13 0 0 12\nH 3 4\nCX 3 0 4 0 14 0 3 1 1 3 3 1 1 15\nH 6\nCX 4 1 6 1 5 2 2 5 5 2\nH 2 3 7 8\nCX 2 3 2 6 2 7 2 8 2 9 2 14 2 15 2 18\nH 13\nCX 13 2 7 3 3 7 7 3\nH 5\nCX 3 5 3 6 3 12 3 15 3 16 3 17 4 3 8 3 4 6 4 14 4 16 8 4 13 5 5 13 13 5 5 7 5 8 5 13 5 16 5 18 6 12 6 16 16 7 7 16 16 7 7 15 9 7 10 7 11 7 17 7 18 7 8 9 8 13 8 15 8 16 8 17 8 18 9 17 16 10 10 16 16 10 10 11 10 15 10 16 10 18 13 10 13 11 11 13 13 11 11 16 11 17 16 12 12 16 16 12 12 15 13 12 17 12 18 12 17 13 13 17 17 13 13 17 16 14 14 16 16 14 15 14 16 14 17 14 18 14 17 15 18 15 18 17 17 18 18 17"

# Normalize the string
normalized_str = circuit_str.replace('\n', ' ')
tokens = [t for t in normalized_str.split(' ') if t.strip()]

ops = []
i = 0
while i < len(tokens):
    op = tokens[i]
    i += 1
    targets = []
    while i < len(tokens) and tokens[i].isdigit():
        targets.append(int(tokens[i]))
        i += 1
    ops.append((op, targets))

# Analyze for spreading
qubit_history = {} # q -> list of (op_index, type)

for idx, (op, targets) in enumerate(ops):
    if op == 'H':
        for t in targets:
            if t not in qubit_history: qubit_history[t] = []
            qubit_history[t].append((idx, 'H'))
    elif op == 'CX':
        for k in range(0, len(targets), 2):
            c = targets[k]
            t = targets[k+1]
            if c not in qubit_history: qubit_history[c] = []
            if t not in qubit_history: qubit_history[t] = []
            qubit_history[c].append((idx, 'C')) # Control spreads X
            qubit_history[t].append((idx, 'T')) # Target spreads Z

# Print high fan-out regions
for q, hist in qubit_history.items():
    run_type = None
    run_count = 0
    start_op = 0
    
    for idx, type_ in hist:
        if type_ == 'H':
            if run_count >= 3:
                print(f"Qubit {q}: {run_type} run of {run_count} (ops {start_op}-{idx-1})")
            run_count = 0
            run_type = None
            continue
            
        if type_ == run_type:
            run_count += 1
        else:
            if run_count >= 3:
                print(f"Qubit {q}: {run_type} run of {run_count} (ops {start_op}-{idx-1})")
            run_type = type_
            run_count = 1
            start_op = idx
            
    if run_count >= 3:
        print(f"Qubit {q}: {run_type} run of {run_count} (end)")
