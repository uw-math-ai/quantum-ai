import re
import sys

# Define circuit string in script to avoid reading issues if possible, but reading is cleaner.
# Assuming circuit.stim exists.

def parse_stim(content):
    ops = []
    # Remove comments and clean up
    content = re.sub(r'#.*', '', content)
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        name = parts[0].upper()
        targets = []
        for t in parts[1:]:
            try:
                targets.append(int(t))
            except ValueError:
                pass 
        
        if name == 'CX':
            if len(targets) % 2 != 0:
                pass # odd CX targets? Stim allows broadcast. But here pairs.
            for i in range(0, len(targets), 2):
                ops.append({'name': 'CX', 'targets': [targets[i], targets[i+1]]})
        elif name in ['H', 'S', 'R', 'M']:
            for t in targets:
                ops.append({'name': name, 'targets': [t]})
        else:
             ops.append({'name': name, 'targets': targets})
    return ops

def main():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: circuit.stim not found")
        return
    
    ops = parse_stim(content)
    
    # Identify runs
    # block_defs: (qubit, start_idx, end_idx)
    block_defs = []
    
    # We iterate and maintain "current open block" for each qubit
    # current_runs[q] = {'start': idx, 'count': 0, 'last_cx': idx}
    current_runs = {}
    
    # Ops list indices
    
    for i, op in enumerate(ops):
        name = op['name']
        targets = op['targets']
        
        # Check for breaks
        if name in ['H', 'S', 'R', 'M']:
            for q in targets:
                if q in current_runs:
                    run = current_runs[q]
                    if run['count'] > 7:
                        block_defs.append((q, run['start'], run['last_cx']))
                    del current_runs[q]
        
        # Check for CX
        if name == 'CX':
            c, t = targets
            
            # Control c
            if c not in current_runs:
                current_runs[c] = {'start': i, 'count': 0, 'last_cx': i}
            
            current_runs[c]['count'] += 1
            current_runs[c]['last_cx'] = i
            
            # Target t does not break run (as per analysis)
    
    # Close any open runs at end
    for q, run in current_runs.items():
        if run['count'] > 7:
            block_defs.append((q, run['start'], run['last_cx']))
            
    # Generate insertions
    # Map index -> list of ops to insert BEFORE
    # Map index -> list of ops to insert AFTER
    
    ins_before = {}
    ins_after = {}
    
    next_ancilla = 125
    flag_qubits = []
    
    # We want to insert 'CX q f' before start and 'CX q f' after end.
    # We sort blocks to ensure deterministic flag assignment?
    # Or just iterate.
    
    # We need to be careful: if multiple blocks start at same index, order of insertions matters?
    # CX q1 f1, CX q2 f2...
    # Since they act on different qubits (q1!=q2, f1!=f2), order doesn't matter.
    
    for q, start, end in block_defs:
        f = next_ancilla
        next_ancilla += 1
        flag_qubits.append(f)
        
        op = {'name': 'CX', 'targets': [q, f]}
        
        if start not in ins_before: ins_before[start] = []
        ins_before[start].append(op)
        
        if end not in ins_after: ins_after[end] = []
        ins_after[end].append(op)
        
    # Construct new ops list
    new_ops = []
    for i, op in enumerate(ops):
        if i in ins_before:
            new_ops.extend(ins_before[i])
        
        new_ops.append(op)
        
        if i in ins_after:
            new_ops.extend(ins_after[i])
            
    # Convert back to Stim string
    lines = []
    # Add flags
    # Initialize flags? Implicit |0> in Stim if new.
    # But usually good to be explicit. 'R' resets.
    # But prompt says "Ancilla qubits must be initialized in |0>".
    # Assuming standard Stim behavior (0).
    
    # H on flags? No, we check Z errors on q -> X on f.
    # Wait, we check X errors on q -> X on f.
    # So f must be sensitive to X.
    # CX q f:
    # If q has X, f gets X.
    # If f starts in |0>, and gets X -> |1>.
    # Measure in Z basis -> 1 (-1).
    # Correct. So f in |0> is correct.
    
    for op in new_ops:
        if op['name'] == 'CX':
            lines.append(f"CX {op['targets'][0]} {op['targets'][1]}")
        else:
            lines.append(f"{op['name']} {' '.join(map(str, op['targets']))}")
            
    # Measure flags
    if flag_qubits:
        lines.append(f"M {' '.join(map(str, flag_qubits))}")
        
    print("\n".join(lines))
    
    # Print flag info to stderr or special marker
    print(f"# FLAGS: {flag_qubits}")

if __name__ == '__main__':
    main()
