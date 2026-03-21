import stim

def append_checks(circuit_file, stabilizers_file, output_file):
    with open(circuit_file, 'r') as f:
        circuit_text = f.read()
    
    with open(stabilizers_file, 'r') as f:
        lines = f.readlines()
        
    next_ancilla = 23
    new_lines = [circuit_text.strip()]
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Check type
        has_x = 'X' in line or 'Y' in line
        has_z = 'Z' in line or 'Y' in line
        
        indices = []
        for i, char in enumerate(line):
            if char != 'I':
                indices.append((i, char))
                
        if not indices: continue
        
        # Determine gadget
        if has_z and not has_x:
            # Z-stabilizer. Measure using Control-Ancilla.
            # Flagged to detect X-injection.
            a = next_ancilla
            f = next_ancilla + 1
            next_ancilla += 2
            
            ops = []
            ops.append(f"H {a}")
            ops.append(f"CX {a} {f}")
            for idx, char in indices:
                ops.append(f"CX {a} {idx}")
            ops.append(f"CX {a} {f}")
            ops.append(f"H {a}")
            ops.append(f"M {a} {f}")
            new_lines.append("\n".join(ops))
            
        elif has_x and not has_z:
            # X-stabilizer. Measure using CZ.
            # CZ a q measures X_q parity.
            # Injects Z-error (from X_a).
            # Flag X_a using CX a f.
            
            a = next_ancilla
            f = next_ancilla + 1
            next_ancilla += 2
            
            ops = []
            ops.append(f"H {a}")
            ops.append(f"CX {a} {f}") # Detect X_a
            for idx, char in indices:
                ops.append(f"CZ {a} {idx}")
            ops.append(f"CX {a} {f}")
            ops.append(f"H {a}")
            ops.append(f"M {a} {f}")
            
            new_lines.append("\n".join(ops))
            
    with open(output_file, 'w') as f:
        f.write("\n".join(new_lines))

append_checks(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_v2.stim",
              r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers_v2.txt",
              r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_ft_v3.stim")
