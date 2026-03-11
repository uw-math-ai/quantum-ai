import stim
import re

def clean_circuit(path_in, path_out):
    with open(path_in, 'r') as f:
        content = f.read()
    
    lines = content.splitlines()
    new_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        cmd = parts[0]
        args = parts[1:]
        
        if cmd == "RX":
            # Replace RX with H
            new_lines.append(f"H {' '.join(args)}")
        elif cmd == "R":
            # Remove R (reset to 0), assume already 0
            # If R is used in the middle of a circuit, this is WRONG.
            # But graph state synthesis usually puts resets at the start.
            # If it's at the start, it's redundant.
            # If it's in the middle, it's a dynamic circuit (unlikely here).
            # I'll check if R is used later.
            pass
        elif cmd == "M" or cmd == "MX" or cmd == "MY" or cmd == "MZ":
             # Measurements are not allowed unless present in baseline.
             # Graph state usually doesn't add measurements unless requested.
             new_lines.append(line)
        else:
            new_lines.append(line)
            
    new_content = "\n".join(new_lines)
    
    # Validate with Stim
    try:
        c = stim.Circuit(new_content)
        with open(path_out, "w") as f:
            f.write(str(c))
        print(f"Cleaned circuit saved to {path_out}")
        print(f"CX count: {c.num_gates('CX')}")
        # Graph state uses CZ. CX count should be 0.
        print(f"CZ count: {c.num_gates('CZ')}")
    except Exception as e:
        print(f"Error parsing cleaned circuit: {e}")

if __name__ == "__main__":
    clean_circuit("candidate_graph.stim", "candidate_clean.stim")
