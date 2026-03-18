import stim
import sys

def parse_circuit(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

def save_circuit(lines, filename):
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

def insert_proxy_control(lines, control, start_idx, end_idx, ancilla):
    # Wraps the CNOTs in lines[start_idx:end_idx+1] with proxy ancilla
    # Assumes these lines are all CX control targets
    # Original: CX c t1 \n CX c t2 ...
    # New:
    # CX c a
    # CX a t1
    # CX a t2
    # ...
    # CX c a
    # M a (implicit? No, must measure at end. But to save space/time, we just leave it for now and measure at end)
    # Actually prompt says "All ancilla qubits must be initialized in |0> and measured at the end"
    
    new_lines = []
    
    # Init ancilla? It's init at start.
    # CX c a
    new_lines.append(f"CX {control} {ancilla}")
    
    for i in range(start_idx, end_idx):
        line = lines[i]
        # Parse line to replace control
        # Line format "CX c t" or "CX c t c t"
        # We need to robustly replace `control` with `ancilla` in the active position
        parts = line.split()
        gate = parts[0]
        args = [int(x) for x in parts[1:]]
        new_args = []
        for j in range(0, len(args), 2):
            c = args[j]
            t = args[j+1]
            if c == control:
                new_args.extend([ancilla, t])
            else:
                new_args.extend([c, t])
        new_lines.append(f"{gate} " + " ".join(str(x) for x in new_args))
        
    # Uncompute
    new_lines.append(f"CX {control} {ancilla}")
    
    return new_lines

# I will implement a more robust modifier that works on the parsed instructions
# rather than lines, to handle multi-target gates
