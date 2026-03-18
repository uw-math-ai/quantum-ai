
import sys
import re

def parse_circuit(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    ops = []
    line_idx = 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        gate = parts[0]
        try:
            qubits = [int(x) for x in parts[1:]]
        except ValueError:
            continue
        # Split multi-qubit gates into single ops for simulation clarity?
        # The prompt says 'H 0 21'. This is H 0 then H 21 (parallel).
        # We can treat them as one 'H' op on [0, 21].
        # But 'CX 0 21 0 42 ...' is CX 0 21, then CX 0 42...
        # Stim treats CX a b c d as (CX a b), (CX c d). Pairs.
        if gate == 'CX':
            pairs = []
            for i in range(0, len(qubits), 2):
                ops.append(('CX', [qubits[i], qubits[i+1]]))
        elif gate == 'H':
            for q in qubits:
                ops.append(('H', [q]))
        else:
            ops.append((gate, qubits))
    return ops

def simulate_faults(ops, num_qubits=63):
    # active_faults: list of Fault objects
    # Fault: {id, type, location, current_pauli_map: {q: P}}
    # This is getting complicated.
    # Let's use sets.
    # We want to know for each (loc, type), what is the final weight.
    # Let's map (loc, type) -> set of qubits with X error, set of qubits with Z error.
    
    # Actually, simpler:
    # Just forward propagate the set of affected qubits for X and Z errors.
    # State: 
    #   x_propagators[q] = set of fault_ids that cause an X error on q
    #   z_propagators[q] = set of fault_ids that cause a Z error on q
    
    x_props = [set() for _ in range(num_qubits)]
    z_props = [set() for _ in range(num_qubits)]
    
    fault_counter = 0
    fault_info = {} # id -> (gate_idx, type, qubit)
    
    for gate_idx, (gate, targets) in enumerate(ops):
        # 1. Update propagators
        if gate == 'H':
            q = targets[0] # H is single qubit in our parsed list
            # Swap X and Z sets
            x_props[q], z_props[q] = z_props[q], x_props[q]
            
        elif gate == 'CX':
            c, t = targets
            # X propagates c -> t
            # Z propagates t -> c
            
            # We need to copy to avoid modifying while iterating?
            # Sets are mutable. Union is safe.
            # But wait, if I add to t, does it affect c later?
            # No, simultaneous update?
            # CX is unitary. It happens.
            # X on c becomes X on c and X on t.
            # So x_props[t] |= x_props[c].
            # Z on t becomes Z on t and Z on c.
            # So z_props[c] |= z_props[t].
            
            new_x_t = x_props[t] | x_props[c]
            new_z_c = z_props[c] | z_props[t]
            
            x_props[t] = new_x_t
            z_props[c] = new_z_c
            
        # 2. Inject new faults
        # X fault on targets
        # Z fault on targets
        for q in targets:
            # Inject X
            fid_x = fault_counter
            fault_counter += 1
            fault_info[fid_x] = (gate_idx, 'X', q)
            x_props[q].add(fid_x)
            
            # Inject Z
            fid_z = fault_counter
            fault_counter += 1
            fault_info[fid_z] = (gate_idx, 'Z', q)
            z_props[q].add(fid_z)
            
    # Count weights
    # For each fault_id, count how many qubits have it in X or Z.
    fault_weights = {}
    
    for q in range(num_qubits):
        for fid in x_props[q]:
            fault_weights[fid] = fault_weights.get(fid, 0) + 1
        for fid in z_props[q]:
            # If a qubit has both X and Z from same fault, it's Y error (weight 1).
            # So we should be careful not to double count.
            # But here we iterate X set then Z set.
            # If fid is in both, we added 1 in X loop, now add 1 in Z loop?
            # No. Weight is number of qubits with non-identity Pauli.
            # So we need to group by fid.
            pass
            
    # Correct counting
    final_errors = {} # fid -> set of qubits
    for q in range(num_qubits):
        for fid in x_props[q]:
            if fid not in final_errors: final_errors[fid] = set()
            final_errors[fid].add(q)
        for fid in z_props[q]:
            if fid not in final_errors: final_errors[fid] = set()
            final_errors[fid].add(q)
            
    bad_faults = []
    for fid, qubits in final_errors.items():
        w = len(qubits)
        if w >= 4:
            bad_faults.append((fid, w, fault_info[fid]))
            
    print(f'Total faults: {fault_counter}')
    print(f'Bad faults: {len(bad_faults)}')
    bad_faults.sort(key=lambda x: x[1], reverse=True)
    for bf in bad_faults[:20]:
        print(f'Weight {bf[1]}: Gate {bf[2][0]} {ops[bf[2][0]]} {bf[2][1]} on Q{bf[2][2]}')

ops = parse_circuit('input_circuit_ft.stim')
simulate_faults(ops)

