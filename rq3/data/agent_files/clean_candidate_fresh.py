import stim

def clean():
    input_file = "candidate_graph_converted.stim"
    output_file = "candidate_clean_fresh.stim"
    
    with open(input_file, "r") as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        l = line.strip()
        if not l:
            continue
        if l.startswith("RX"):
            # Replace RX with H
            # And split into multiple lines to avoid wrapping
            qubits = l.split()[1:]
            # Chunking
            chunk_size = 20
            for i in range(0, len(qubits), chunk_size):
                chunk = qubits[i:i+chunk_size]
                new_lines.append(f"H {' '.join(chunk)}")
        elif l == "TICK":
            continue
        elif len(l) > 100:
             # Check if it's a long gate line
             parts = l.split()
             gate = parts[0]
             args = parts[1:]
             chunk_size = 20
             for i in range(0, len(args), chunk_size):
                 chunk = args[i:i+chunk_size]
                 new_lines.append(f"{gate} {' '.join(chunk)}")
        else:
            new_lines.append(l)
            
    with open(output_file, "w") as f:
        f.write("\n".join(new_lines))
        
    print(f"Wrote {len(new_lines)} lines to {output_file}")

if __name__ == "__main__":
    clean()
