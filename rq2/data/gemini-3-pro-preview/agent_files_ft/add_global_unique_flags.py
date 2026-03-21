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

flag_start = 49
current_flag = flag_start
flags = []

new_lines = []

for name, targets in gates:
    if name == 'CX':
        for i in range(0, len(targets), 2):
            c = targets[i]
            t = targets[i+1]
            
            # Use two unique flags per CX
            fc = current_flag
            current_flag += 1
            ft = current_flag
            current_flag += 1
            flags.extend([fc, ft])
            
            # Sandwich
            new_lines.append(f"CX {c} {fc}") # Check c
            new_lines.append(f"CX {t} {ft}") # Check t
            new_lines.append(f"CX {c} {t}")  # Op
            new_lines.append(f"CX {t} {ft}") # Check t
            new_lines.append(f"CX {c} {fc}") # Check c
            
    elif name == 'H':
        for t in targets:
            new_lines.append(f"H {t}")
            # No sandwich for H itself, relies on next CX sandwich
    else:
        pass

circuit_str = "\n".join(new_lines)
print(circuit_str)
print(f"FLAGS:{flags}")
