import re

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

gates = parse_circuit(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\baseline.stim')

# Linearize
linear_ops = []
for name, targets in gates:
    if name == 'CX':
        for i in range(0, len(targets), 2):
            linear_ops.append(('CX', targets[i], targets[i+1]))
    elif name == 'H':
        for t in targets:
            linear_ops.append(('H', t))
    else:
        linear_ops.append((name, targets))

# Identify runs
runs = []
current_control = None
run_start = 0

for i, op in enumerate(linear_ops):
    if op[0] == 'CX':
        ctrl = op[1]
        if ctrl == current_control:
            pass
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

long_runs = [r for r in runs if r[2] - r[1] >= 4]

# Sort runs by start index reverse to insert safely?
# No, we will rebuild the list.

new_ops = []
flag_qubit = 49
flags = []

run_map = {r[1]: r for r in long_runs} # Key by start index

i = 0
while i < len(linear_ops):
    if i in run_map:
        # Start of a run
        ctrl, start, end, length = *run_map[i], run_map[i][2]-run_map[i][1]
        # Insert start flag
        f = flag_qubit
        flag_qubit += 1
        flags.append(f)
        
        # Add the sandwich start
        new_ops.append(('CX', ctrl, f))
        
        # Add the run
        for k in range(start, end):
            new_ops.append(linear_ops[k])
            
        # Add the sandwich end
        new_ops.append(('CX', ctrl, f))
        
        i = end
    else:
        new_ops.append(linear_ops[i])
        i += 1

# Reconstruct Stim format
lines = []
for op in new_ops:
    if op[0] == 'CX':
        lines.append(f"CX {op[1]} {op[2]}")
    elif op[0] == 'H':
        lines.append(f"H {op[1]}")
    else:
        # Handle other gates if any (none in baseline)
        pass

# Output circuit
circuit_str = "\n".join(lines)
print(circuit_str)
print(f"FLAGS:{flags}")
