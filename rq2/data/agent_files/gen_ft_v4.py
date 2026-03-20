import sys
import re

def parse_circuit_ops(circuit_str):
    lines = circuit_str.strip().split('\n')
    ops = []
    original_idx = 0
    for line in lines:
        parts = line.split()
        if not parts: continue
        name = parts[0]
        targets = []
        for t in parts[1:]:
             try:
                 val = int(t)
                 targets.append(val)
             except:
                 pass
        
        if name == 'CX' or name == 'CNOT':
            for i in range(0, len(targets), 2):
                ops.append(['CX', targets[i], targets[i+1]])
        elif name == 'H':
            for t in targets:
                ops.append(['H', [t]])
        else:
            ops.append([name, targets])
    return ops

def analyze_and_patch(circuit_str):
    ops = parse_circuit_ops(circuit_str)
    
    # Pre-calculate chains
    qubit_chains = {} # q -> list of (op_index, type)
    
    for i, op in enumerate(ops):
        name = op[0]
        if name == 'CX':
            c, t = op[1], op[2]
            if c not in qubit_chains: qubit_chains[c] = []
            if t not in qubit_chains: qubit_chains[t] = []
            qubit_chains[c].append((i, 'c'))
            qubit_chains[t].append((i, 't'))
        else:
             qs = op[1]
             for q in qs:
                 if q not in qubit_chains: qubit_chains[q] = []
                 qubit_chains[q].append((i, 'break'))

    flags_to_insert = [] # list of (before_op_index, priority, text)
    # Priority: lower number = earlier insertion
    
    # Determine max qubit index to allocate ancillas
    max_q = 62
    for op in ops:
        if op[0] == 'CX':
            max_q = max(max_q, op[1], op[2])
        else:
            if op[1]: max_q = max(max_q, max(op[1]))
            
    next_ancilla = max_q + 1
    
    for q, chain in qubit_chains.items():
        # Identify continuous segments
        segments = []
        current_type = None
        current_segment = []
        
        for item in chain:
            idx, type_ = item
            if type_ == 'break':
                if current_segment:
                    segments.append((current_type, current_segment))
                    current_segment = []
                current_type = None
            else:
                if current_type is None:
                    current_type = type_
                    current_segment.append(idx)
                elif current_type == type_:
                    current_segment.append(idx)
                else:
                    if current_segment:
                        segments.append((current_type, current_segment))
                    current_segment = [idx]
                    current_type = type_
        if current_segment:
            segments.append((current_type, current_segment))
            
        # Process segments
        for type_, segment in segments:
            count = len(segment)
            idx = 0
            open_flag = None # (ancilla_idx, type)
            
            # Process in chunks of 2
            while idx < count:
                needed = (count - idx >= 3)
                current_op_index = segment[idx]
                
                # Close old flag?
                # Close BEFORE current op (so it covers gap, but not current op)
                # But wait, if we start new flag, we want overlap.
                # Start New (Priority 1)
                # Close Old (Priority 2)
                
                new_flag_idx = None
                
                if needed:
                    new_flag_idx = next_ancilla
                    next_ancilla += 1
                    
                    if type_ == 'c':
                         # X check: CX q f. f in |0>
                         check_op = f"CX {q} {new_flag_idx}"
                         setup = check_op
                    else:
                         # Z check: CX f q. f in |+>
                         check_op = f"CX {new_flag_idx} {q}"
                         setup = f"H {new_flag_idx}\n{check_op}"
                    
                    flags_to_insert.append((current_op_index, 1, setup))
                
                if open_flag is not None:
                     f_q, f_type = open_flag
                     
                     if f_type == 'c':
                         teardown = f"CX {q} {f_q}\nM {f_q}"
                     else:
                         teardown = f"CX {f_q} {q}\nH {f_q}\nM {f_q}"
                     
                     flags_to_insert.append((current_op_index, 2, teardown))
                     open_flag = None
                
                if new_flag_idx is not None:
                    open_flag = (new_flag_idx, type_)
                
                idx += 2
            
            # Close pending flag after segment
            if open_flag is not None:
                last_op_index = segment[-1]
                insertion_idx = last_op_index + 1
                
                f_q, f_type = open_flag
                if f_type == 'c':
                     teardown = f"CX {q} {f_q}\nM {f_q}"
                else:
                     teardown = f"CX {f_q} {q}\nH {f_q}\nM {f_q}"
                
                flags_to_insert.append((insertion_idx, 1, teardown))

    # Reconstruct
    flags_to_insert.sort(key=lambda x: (x[0], x[1]))
    
    new_circuit_lines = []
    
    flag_ptr = 0
    N = len(ops)
    
    for i in range(N + 1):
        while flag_ptr < len(flags_to_insert) and flags_to_insert[flag_ptr][0] == i:
            new_circuit_lines.append(flags_to_insert[flag_ptr][2])
            flag_ptr += 1
            
        if i < N:
            op = ops[i]
            if op[0] == 'CX':
                new_circuit_lines.append(f"CX {op[1]} {op[2]}")
            elif op[0] == 'H':
                targets = " ".join(str(x) for x in op[1])
                new_circuit_lines.append(f"H {targets}")
            else:
                targets = " ".join(str(x) for x in op[1])
                new_circuit_lines.append(f"{op[0]} {targets}")
                
    return "\n".join(new_circuit_lines)

if __name__ == "__main__":
    with open("circuit.stim", "r") as f:
        content = f.read()
    
    new_c = analyze_and_patch(content)
    
    with open("circuit_ft.stim", "w") as f:
        f.write(new_c)
        
    all_ints = [int(x) for x in re.findall(r'\d+', new_c)]
    max_q = max(all_ints) if all_ints else 0
    # data qubits are 0..62. Ancillas are 63..max_q
    ancillas = list(range(63, max_q + 1))
    
    with open("ancillas.txt", "w") as f:
        f.write(" ".join(map(str, ancillas)))
