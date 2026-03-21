
import sys

circuit_str = "CX 13 0 0 13 13 0 0 12\nH 3 4\nCX 3 0 4 0 14 0 3 1 1 3 3 1 1 15\nH 6\nCX 4 1 6 1 5 2 2 5 5 2\nH 2 3 7 8\nCX 2 3 2 6 2 7 2 8 2 9 2 14 2 15 2 18\nH 13\nCX 13 2 7 3 3 7 7 3\nH 5\nCX 3 5 3 6 3 12 3 15 3 16 3 17 4 3 8 3 4 6 4 14 4 16 8 4 13 5 5 13 13 5 5 7 5 8 5 13 5 16 5 18 6 12 6 16 16 7 7 16 16 7 7 15 9 7 10 7 11 7 17 7 18 7 8 9 8 13 8 15 8 16 8 17 8 18 9 17 16 10 10 16 16 10 10 11 10 15 10 16 10 18 13 10 13 11 11 13 13 11 11 16 11 17 16 12 12 16 16 12 12 15 13 12 17 12 18 12 17 13 13 17 17 13 13 17 16 14 14 16 16 14 15 14 16 14 17 14 18 14 17 15 18 15 18 17 17 18 18 17"

normalized_str = circuit_str.replace('\n', ' ')
tokens = [t for t in normalized_str.split(' ') if t.strip()]

atomic_ops = []
i = 0
max_qubit = 0
while i < len(tokens):
    op = tokens[i]
    i += 1
    if op == 'CX':
        targets = []
        while i < len(tokens) and tokens[i].isdigit():
            targets.append(int(tokens[i]))
            i += 1
        for k in range(0, len(targets), 2):
            c = targets[k]
            t = targets[k+1]
            atomic_ops.append(('CX', c, t))
            max_qubit = max(max_qubit, c, t)
    elif op == 'H':
        targets = []
        while i < len(tokens) and tokens[i].isdigit():
            targets.append(int(tokens[i]))
            i += 1
        for t in targets:
            atomic_ops.append(('H', t))
            max_qubit = max(max_qubit, t)

runs = []
current_runs = {}

for idx, op_data in enumerate(atomic_ops):
    op_type = op_data[0]
    involved_qubits = []
    if op_type == 'CX':
        c, t = op_data[1], op_data[2]
        involved_qubits = [(c, 'C'), (t, 'T')]
    elif op_type == 'H':
        t = op_data[1]
        involved_qubits = [(t, 'H')]
        
    for q, role in involved_qubits:
        if q in current_runs:
            run_type, start, count = current_runs[q]
            if role == run_type:
                current_runs[q] = (run_type, start, count + 1)
            else:
                if count >= 1:
                    runs.append((run_type, q, start, idx - 1))
                del current_runs[q]
                if role in ['C', 'T']:
                    current_runs[q] = (role, idx, 1)
        else:
            if role in ['C', 'T']:
                current_runs[q] = (role, idx, 1)

for q, (run_type, start, count) in current_runs.items():
    runs.append((run_type, q, start, len(atomic_ops) - 1))

critical_qubits = {0, 1, 2, 3, 13, 15}
filtered_runs = []
for r in runs:
    r_type, q, start, end = r
    count = (end - start) + 1
    threshold = 2
    if q in critical_qubits:
        threshold = 1
    if count >= threshold:
        filtered_runs.append(r)

next_ancilla = max_qubit + 1
insertions = []

# Helper to add insertion
def add_ins(idx, s):
    insertions.append((idx, s))

for r_type, q, start, end in filtered_runs:
    # Standard flags
    flag1 = next_ancilla
    next_ancilla += 1
    
    if r_type == 'C':
        # Standard X-monitor for C-run
        add_ins(start, f"CX {q} {flag1}")
        add_ins(end + 1, f"CX {q} {flag1}\nM {flag1}")
    elif r_type == 'T':
        # Standard Z-monitor for T-run
        add_ins(start, f"H {flag1}\nCX {flag1} {q}")
        add_ins(end + 1, f"CX {flag1} {q}\nH {flag1}\nM {flag1}")
        
    # Compensated flags for critical
    if q in critical_qubits:
        flag2 = next_ancilla
        next_ancilla += 1
        
        # Collect intervening ops
        intervening_ops = atomic_ops[start:end+1]
        
        if r_type == 'T':
            # Add Compensated X-monitor
            # Pre
            insertions.append((start, f"CX {q} {flag2}"))
            
            # Compensation
            # X on Control (c) spreads to Target (q).
            # We must update flag2 with X_c.
            # For each op CX c q:
            # Add CX c f2.
            
            for k, op in enumerate(intervening_ops):
                abs_idx = start + k
                if op[0] == 'CX':
                    c = op[1]
                    # Insert CX c f2
                    insertions.append((abs_idx, f"CX {c} {flag2}"))
            
            # Post
            insertions.append((end + 1, f"CX {q} {flag2}\nM {flag2}"))

        elif r_type == 'C':
            # Add Compensated Z-monitor
            # Pre
            add_ins(start, f"H {flag2}\nCX {flag2} {q}")
            
            # Compensation
            # Z on Control (q) is STABLE ($Z_C \to Z_C$).
            # So Z-monitor on Control is STABLE.
            # Does it need compensation?
            # "CX fZ q injects X into q".
            # X on q (Control) spreads to Target.
            # So we MUST compensate the INJECTED X on Targets.
            # For each op `CX q t`:
            # We need `CX f2 t`.
            
            for k, op in enumerate(intervening_ops):
                abs_idx = start + k
                # op is ('CX', q, t)
                if op[0] == 'CX' and op[1] == q:
                    t = op[2]
                    # Insert compensation CX f2 t
                    add_ins(abs_idx, f"CX {flag2} {t}")
            
            # Post
            add_ins(end + 1, f"CX {flag2} {q}\nH {flag2}\nM {flag2}")

insertions.sort(key=lambda x: x[0])

final_ops = []
current_idx = 0
ins_ptr = 0

while current_idx <= len(atomic_ops):
    while ins_ptr < len(insertions) and insertions[ins_ptr][0] == current_idx:
        final_ops.append(insertions[ins_ptr][1])
        ins_ptr += 1
    
    if current_idx < len(atomic_ops):
        op = atomic_ops[current_idx]
        if op[0] == 'CX':
            final_ops.append(f"CX {op[1]} {op[2]}")
        else:
            final_ops.append(f"H {op[1]}")
    current_idx += 1

print("\n".join(final_ops))
