import stim
import os

def clean():
    input_file = "my_candidate_graph.stim"
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return

    with open(input_file, "r") as f:
        content = f.read()

    new_lines = []
    total_cz_edges = 0
    
    for line in content.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("TICK"): continue
        
        parts = line.split()
        if parts[0] == "RX":
            # RX targets -> H targets
            # Check if all targets are integers
            try:
                [int(x) for x in parts[1:]]
                new_line = "H " + " ".join(parts[1:])
                new_lines.append(new_line)
            except ValueError:
                # Might be "RX(0.1)" or something else? Stim uses gate names.
                # "RX" is "Reset X".
                new_lines.append(line)
        elif parts[0] == "CZ":
            # CZ targets
            targets = parts[1:]
            # Pairs
            total_cz_edges += len(targets) // 2
            new_lines.append(line)
        else:
            new_lines.append(line)

    print(f"Total CZ edges: {total_cz_edges}")
    
    clean_content = "\n".join(new_lines)
    
    output_file = "my_candidate_graph_clean.stim"
    with open(output_file, "w") as f:
        f.write(clean_content)
    print(f"Written to {output_file}")
    
    # Verify parsing
    try:
        c = stim.Circuit(clean_content)
        print("Parsing successful.")
        print(f"Circuit length: {len(c)}")
    except Exception as e:
        print(f"Parsing failed: {e}")

if __name__ == "__main__":
    clean()
