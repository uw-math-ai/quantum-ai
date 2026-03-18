import re

def parse_circuit(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Simple parser for the provided format
    # Assumes "GATE t1 t2..." or "CX c1 t1 c2 t2..."
    tokens = content.split()
    expanded = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == 'CX':
            i += 1
            # Next are pairs
            while i < len(tokens) and tokens[i] not in ['CX', 'H']:
                c = int(tokens[i])
                t = int(tokens[i+1])
                expanded.append({'gate': 'CX', 'targets': [c, t]})
                i += 2
        elif token == 'H':
            i += 1
            while i < len(tokens) and tokens[i] not in ['CX', 'H']:
                t = int(tokens[i])
                expanded.append({'gate': 'H', 'targets': [t]})
                i += 1
        else:
            i += 1
    return expanded

def is_swap(chunk):
    # Check if a list of 3 CX gates is a SWAP: CX a b, CX b a, CX a b
    if len(chunk) < 3:
        return False
    g1, g2, g3 = chunk[0], chunk[1], chunk[2]
    if g1['gate'] != 'CX' or g2['gate'] != 'CX' or g3['gate'] != 'CX':
        return False
    a, b = g1['targets']
    if g2['targets'] == [b, a] and g3['targets'] == [a, b]:
        return True
    return False

def optimize_circuit(ops, start_ancilla):
    new_ops = []
    flag_qubits = []
    next_ancilla = start_ancilla
    
    i = 0
    while i < len(ops):
        # Check for SWAP (3 CXs)
        if i + 2 < len(ops):
            chunk = ops[i:i+3]
            if is_swap(chunk):
                new_ops.extend(chunk)
                i += 3
                continue
        
        op = ops[i]
        if op['gate'] == 'H':
            new_ops.append(op)
            i += 1
            continue
            
        # It's a single CX. Check if next ones are also CX with same control
        # and NOT part of a SWAP
        if op['gate'] == 'CX':
            control = op['targets'][0]
            targets = [op['targets'][1]]
            
            j = i + 1
            while j < len(ops):
                next_op = ops[j]
                
                # Must be CX
                if next_op['gate'] != 'CX':
                    break
                
                # Check if this op starts a SWAP
                if j + 2 < len(ops):
                    chunk = ops[j:j+3]
                    if is_swap(chunk):
                        break
                
                # Check control matches
                if next_op['targets'][0] == control:
                    targets.append(next_op['targets'][1])
                    j += 1
                else:
                    break
            
            # Now we have a block of CXs from `control` to `targets`
            # count = j - i
            if len(targets) >= 2:
                # Apply Gadget
                flag = next_ancilla
                next_ancilla += 1
                flag_qubits.append(flag)
                
                # CX c f
                new_ops.append({'gate': 'CX', 'targets': [control, flag]})
                # CX f t1, CX f t2...
                for t in targets:
                    new_ops.append({'gate': 'CX', 'targets': [flag, t]})
                # CX c f
                new_ops.append({'gate': 'CX', 'targets': [control, flag]})
                
                i = j
            else:
                # Just one CX, or not a fanout block
                new_ops.append(op)
                i += 1
        else:
            new_ops.append(op)
            i += 1
                
    return new_ops, flag_qubits

def ops_to_stim(ops):
    lines = []
    for op in ops:
        if op['gate'] == 'CX':
            lines.append(f"CX {op['targets'][0]} {op['targets'][1]}")
        else:
            lines.append(f"H {op['targets'][0]}")
    return "\n".join(lines)

ops = parse_circuit('input_circuit_correct.stim')
print(f"DEBUG: start_ancilla={28}")
final_ops, flags = optimize_circuit(ops, 28)

with open('candidate_v1.stim', 'w') as f:
    f.write(ops_to_stim(final_ops))

with open('ancillas.txt', 'w') as f:
    f.write(",".join(map(str, flags)))
