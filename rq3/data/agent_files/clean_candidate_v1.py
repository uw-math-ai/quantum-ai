import sys

def clean():
    input_file = "candidate_v1.stim"
    output_file = "candidate_v1_clean.stim"
    
    with open(input_file, "r") as f:
        lines = f.readlines()
        
    circuit_lines = []
    start = False
    for line in lines:
        if line.strip().startswith("Done."):
            start = True
            continue
        if start:
            # Check if line is a valid stim instruction
            l = line.strip()
            if not l: continue
            circuit_lines.append(l)

    with open(output_file, "w") as f:
        for line in circuit_lines:
            if line.startswith("CZ"):
                parts = line.split()
                cmd = parts[0]
                args = parts[1:]
                # Group args into pairs
                pairs = [args[i:i+2] for i in range(0, len(args), 2)]
                # Write each pair as a separate CZ instruction or group them
                # To be safe and readable, let's write chunks
                chunk_size = 10 # 10 pairs per line
                for i in range(0, len(pairs), chunk_size):
                    chunk = pairs[i:i+chunk_size]
                    flat_chunk = [item for sublist in chunk for item in sublist]
                    f.write(f"CZ {' '.join(flat_chunk)}\n")
            else:
                f.write(line + "\n")

if __name__ == "__main__":
    clean()
