import sys

try:
    with open("candidate.stim", "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("RX"):
            # Replace RX with H
            parts = line.split()
            qubits = parts[1:]
            new_lines.append(f"H {' '.join(qubits)}")
        elif line == "TICK":
            continue
        else:
            new_lines.append(line)

    with open("candidate_final_graph.stim", "w") as f:
        f.write("\n".join(new_lines))
        
    print("Cleaned candidate saved to candidate_final_graph.stim")

except Exception as e:
    print(f"Error: {e}")
