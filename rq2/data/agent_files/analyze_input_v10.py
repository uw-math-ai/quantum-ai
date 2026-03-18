import sys
import re

def parse_circuit(filename):
    ops = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    current_op_idx = 0
    for line_idx, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        gate = parts[0]
        try:
            qubits = [int(x) for x in parts[1:]]
        except ValueError:
            continue
        
        if gate == 'CX':
            # CX c1 t1 c2 t2 ...
            for i in range(0, len(qubits), 2):
                c = qubits[i]
                t = qubits[i+1]
                ops.append({'gate': 'CX', 'targets': [c, t], 'line': line_idx, 'idx': current_op_idx})
                current_op_idx += 1
        elif gate == 'H':
            for q in qubits:
                ops.append({'gate': 'H', 'targets': [q], 'line': line_idx, 'idx': current_op_idx})
                current_op_idx += 1
        else:
            # Ignore other gates for now or treat as identity for error prop
            pass
            
    return ops

def analyze(ops, num_qubits=120):
    # active_faults: set of (fault_id) for each qubit
    # fault_id = (op_idx, type, qubit)
    
    # We want to know which faults propagate to >= 7 qubits.
    
    # State: 
    # x_set[q] = set of fault_ids
    # z_set[q] = set of fault_ids
    
    x_set = [set() for _ in range(num_qubits)]
    z_set = [set() for _ in range(num_qubits)]
    
    # Tracking faults
    all_faults = [] # list of (op_idx, type, qubit)
    
    for op in ops:
        gate = op['gate']
        targets = op['targets']
        idx = op['idx']
        
        # 1. Inject new faults at input of this gate
        for q in targets:
            # Inject X
            fid_x = (idx, 'X', q)
            all_faults.append(fid_x)
            x_set[q].add(fid_x)
            
            # Inject Z
            fid_z = (idx, 'Z', q)
            all_faults.append(fid_z)
            z_set[q].add(fid_z)
            
        # 2. Propagate
        if gate == 'H':
            q = targets[0]
            # Swap
            x_set[q], z_set[q] = z_set[q], x_set[q]
            
        elif gate == 'CX':
            c, t = targets
            # X: c -> t
            # Z: t -> c
            
            # Use copy to avoid modifying while iterating?
            # Sets are mutable.
            # new_x_t = x_t | x_c
            # new_z_c = z_c | z_t
            
            # We can update in place if order matters?
            # c affects t.
            # t affects c.
            # Simultaneous? Yes, unitary.
            
            xc = x_set[c]
            xt = x_set[t]
            zc = z_set[c]
            zt = z_set[t]
            
            x_set[t] = xt | xc
            z_set[c] = zc | zt
            
    # Count results
    # fault_id -> set of affected qubits
    fault_map = {}
    
    for q in range(num_qubits):
        # Errors on q
        # X errors
        for fid in x_set[q]:
            if fid not in fault_map: fault_map[fid] = set()
            fault_map[fid].add(q)
        # Z errors
        for fid in z_set[q]:
            if fid not in fault_map: fault_map[fid] = set()
            fault_map[fid].add(q)
            
    bad_count = 0
    bad_list = []
    
    for fid, qubits in fault_map.items():
        w = len(qubits)
        if w >= 7:
            bad_count += 1
            bad_list.append((w, fid))
            
    bad_list.sort(reverse=True)
    
    print(f"Total faults: {len(all_faults)}")
    print(f"Bad faults (>=7): {bad_count}")
    
    for w, fid in bad_list[:10]:
        op_idx, ftype, q = fid
        # find op
        op = next(o for o in ops if o['idx'] == op_idx)
        print(f"Weight {w}: {ftype} on Q{q} at Op {op_idx} ({op['gate']} {op['targets']}) Line {op['line']}")

if __name__ == '__main__':
    ops = parse_circuit('input_circuit_v9_ft.stim')
    analyze(ops)
