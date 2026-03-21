import stim

def parse_circuit(filename):
    c = stim.Circuit.from_file(filename)
    ops = []
    for instruction in c:
        if instruction.name == "CX" or instruction.name == "CNOT":
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                c_val = targets[i].value
                t_val = targets[i+1].value
                ops.append({'type': 'CX', 'c': c_val, 't': t_val})
        elif instruction.name == "H":
            targets = instruction.targets_copy()
            for t in targets:
                ops.append({'type': 'H', 'q': t.value})
    return ops

def find_sequences(ops, threshold=1):
    sequences = []
    max_q = 0
    for op in ops:
        if op['type'] == 'CX':
            max_q = max(max_q, op['c'], op['t'])
        elif op['type'] == 'H':
            max_q = max(max_q, op['q'])
            
    for q in range(max_q + 1):
        start = -1
        count = 0
        for i, op in enumerate(ops):
            if op['type'] == 'CX':
                if op['c'] == q:
                    if start == -1: start = i
                    count += 1
                elif op['t'] == q:
                    if count >= threshold:
                        sequences.append({'type': 'control', 'qubit': q, 'start': start, 'end': i})
                    start = -1
                    count = 0
            elif op['type'] == 'H':
                if op['q'] == q:
                    if count >= threshold:
                        sequences.append({'type': 'control', 'qubit': q, 'start': start, 'end': i})
                    start = -1
                    count = 0
        if count >= threshold:
             sequences.append({'type': 'control', 'qubit': q, 'start': start, 'end': len(ops)})
             
    for q in range(max_q + 1):
        start = -1
        count = 0
        for i, op in enumerate(ops):
            if op['type'] == 'CX':
                if op['t'] == q:
                    if start == -1: start = i
                    count += 1
                elif op['c'] == q:
                    if count >= threshold:
                        sequences.append({'type': 'target', 'qubit': q, 'start': start, 'end': i})
                    start = -1
                    count = 0
            elif op['type'] == 'H':
                if op['q'] == q:
                    if count >= threshold:
                        sequences.append({'type': 'target', 'qubit': q, 'start': start, 'end': i})
                    start = -1
                    count = 0
        if count >= threshold:
             sequences.append({'type': 'target', 'qubit': q, 'start': start, 'end': len(ops)})
             
    return sequences

def generate_flagged_circuit(ops, sequences, flag_start_idx=63):
    insertions = {}
    current_flag = flag_start_idx
    used_flags = set()
    
    for seq in sequences:
        f = current_flag
        current_flag += 1
        used_flags.add(f)
        
        if seq['start'] not in insertions: insertions[seq['start']] = {'before': [], 'after': []}
        last_idx = seq['end'] - 1
        if last_idx not in insertions: insertions[last_idx] = {'before': [], 'after': []}
        
        if seq['type'] == 'control':
            insertions[seq['start']]['before'].append(f"CX {seq['qubit']} {f}")
            insertions[last_idx]['after'].append(f"CX {seq['qubit']} {f}")
        elif seq['type'] == 'target':
            insertions[seq['start']]['before'].append(f"H {f}")
            insertions[seq['start']]['before'].append(f"CX {f} {seq['qubit']}")
            
            insertions[last_idx]['after'].append(f"CX {f} {seq['qubit']}")
            insertions[last_idx]['after'].append(f"H {f}")
            
    lines = []
    for i, op in enumerate(ops):
        if i in insertions:
            lines.extend(insertions[i]['before'])
        
        if op['type'] == 'CX':
            lines.append(f"CX {op['c']} {op['t']}")
        elif op['type'] == 'H':
            lines.append(f"H {op['q']}")
            
        if i in insertions:
            lines.extend(insertions[i]['after'])
            
    for f in sorted(list(used_flags)):
        lines.append(f"M {f}")
        
    return "\n".join(lines)

def main():
    with open("circuit.stim", "w") as f:
        f.write("""CX 9 0 0 9 9 0
H 0
CX 0 27 0 36
H 9
CX 9 0 56 1 1 56 56 1 1 27 1 57
H 54 55
CX 9 1 28 1 45 1 46 1 54 1 55 1 62 1 45 2 2 45 45 2 2 36
H 18
CX 9 2 18 2 27 2 28 2 46 2 54 2 55 2 62 2 9 3 3 9 9 3 18 3 27 4 4 27 27 4 18 4 28 4 46 4 54 4 55 4 62 4 18 5 5 18 18 5 36 6 6 36 36 6 56 7 7 56 56 7
H 7 19
CX 7 19 7 28 7 37 7 62
H 10
CX 10 7 28 8 8 28 28 8 8 57 54 8 55 8 10 9 9 10 10 9 9 46 9 57 19 9 54 9 55 9 19 10 10 19 19 10 10 37 10 57 10 62 46 11 11 46 46 11 11 37 11 57 54 11 55 11 62 11 62 12 12 62 62 12 12 37 12 57 37 13 13 37 37 13 46 14 14 46 46 14
H 14
CX 14 29 14 38
H 45
CX 45 14 45 15 15 45 45 15 15 38 15 57 54 15 55 15 29 16 16 29 29 16 16 38 16 47 16 57
H 20
CX 20 16 47 16 54 16 55 16 57 16 57 17 17 57 57 17 17 38 20 17 47 17 47 18 18 47 47 18 20 18 54 18 55 18 20 19 19 20 20 19 38 20 20 38 38 20 62 21 21 62 62 21
H 21 62
CX 21 30 21 39 21 62
H 38
CX 38 21 38 22 22 38 38 22 22 39 22 58 22 59 22 62 54 22 62 23 23 62 62 23 23 30 23 39 23 48 23 58 23 59 54 23 30 24 24 30 30 24 24 48 58 25 25 58 58 25 25 39 25 48 25 59 40 25 54 25 48 26 26 48 48 26 40 26 39 27 27 39 39 27 40 27 39 28 28 39 39 28
H 28 46 47 62
CX 28 31 28 40 28 46 28 47 28 54 28 62
H 37
CX 37 28 54 29 29 54 54 29
H 38
CX 29 31 29 38 29 46 29 47 29 59 29 62 38 30 30 38 38 30 30 31 30 40 30 49 30 59 37 30 31 49 40 32 32 40 40 32 32 49 32 59 37 32 49 33 33 49 49 33 37 34 34 37 37 34 46 35 35 46 46 35 35 40 35 41 35 62 47 35 47 36 36 47 47 36 36 41 36 59 36 62 62 37 37 62 62 37 37 40 37 41 37 50 37 59 40 38 38 40 40 38 38 50 59 39 39 59 59 39 39 41 39 50 50 40 40 50 50 40 45 42 42 45 45 42
H 42 50
CX 42 45 42 49 42 50
H 47
CX 47 42 47 43 43 47 47 43 43 45 43 50 43 60 43 61 55 43 50 44 44 50 50 44 44 45 44 49 44 51 44 60 44 61 55 44 49 45 45 49 49 45 45 51 60 46 46 60 60 46 46 49 46 51 46 61 47 46 55 46 51 47 47 51 51 47 51 47 49 48 48 49 49 48 51 48 56 49 49 56 56 49
H 49 56 57 59
CX 49 51 49 55 49 56 49 57 49 59 49 62
H 54
CX 54 49 55 50 50 55 55 50
H 58
CX 50 56 50 57 50 58 50 59 50 61 50 62 58 51 51 58 58 51 51 52 51 58 51 61 51 62 54 51 62 52 52 62 62 52 52 62 58 53 53 58 58 53 53 61 53 62 54 53 62 54 54 62 62 54 62 55 55 62 62 55 57 56 56 57 57 56 56 57 56 60 56 62 59 56 59 57 57 59 59 57 57 59 57 61 57 62 59 58 58 59 59 58 58 59 58 60 58 61 58 62 60 59 59 60 60 59 59 60 61 60 60 61 61 60 60 61 60 62""")

    ops = parse_circuit("circuit.stim")
    sequences = find_sequences(ops, threshold=1)
    
    print(f"Found {len(sequences)} sequences with threshold 1")
    
    new_circuit = generate_flagged_circuit(ops, sequences)
    
    with open("candidate.stim", "w") as f:
        f.write(new_circuit)
        
if __name__ == "__main__":
    main()
