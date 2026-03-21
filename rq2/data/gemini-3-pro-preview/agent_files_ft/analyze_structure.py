import re
from collections import defaultdict

filename = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\baseline.stim'

def parse_circuit(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    gates = []
    for line in lines:
        parts = line.strip().split()
        if not parts: continue
        name = parts[0]
        targets = [int(x) for x in parts[1:]]
        gates.append((name, targets))
    return gates

gates = parse_circuit(filename)

linear_ops = []
for name, targets in gates:
    if name == 'CX':
        for i in range(0, len(targets), 2):
            linear_ops.append(('CX', targets[i], targets[i+1]))
    elif name == 'H':
        for t in targets:
            linear_ops.append(('H', t))
    else:
        # Assuming other gates don't matter for this analysis or are single qubit
        pass

# Scan for long runs
current_control = None
run_start = 0
runs = []

for i, op in enumerate(linear_ops):
    if op[0] == 'CX':
        ctrl = op[1]
        if ctrl == current_control:
            pass # continuing run
        else:
            if current_control is not None:
                runs.append((current_control, run_start, i))
            current_control = ctrl
            run_start = i
    else:
        if current_control is not None:
            runs.append((current_control, run_start, i))
        current_control = None
        run_start = i + 1

if current_control is not None:
    runs.append((current_control, run_start, len(linear_ops)))

# Filter runs
long_runs = []
for r in runs:
    length = r[2] - r[1]
    if length >= 4:
        long_runs.append((r[0], r[1], r[2], length))

print("Long CX runs (control, start_idx, end_idx, length):")
for r in long_runs:
    print(f"Control {r[0]}: length {r[3]} at {r[1]}-{r[2]}")

max_q = 0
for op in linear_ops:
    if op[0] == 'CX':
        max_q = max(max_q, op[1], op[2])
    elif op[0] == 'H':
        max_q = max(max_q, op[1])
print(f"Max qubit index: {max_q}")
