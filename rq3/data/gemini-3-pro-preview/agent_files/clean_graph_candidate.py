
import re

input_path = r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\candidate_graph.stim"
output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\candidate_graph_clean.stim"

with open(input_path, 'r') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []

for line in lines:
    line = line.strip()
    if not line:
        continue
    if line.startswith("TICK"):
        continue
    if line.startswith("RX"):
        # Replace RX with H
        # The line is "RX 0 1 ... 149"
        # We want "H 0 1 ... 149"
        # Check if it is indeed RX
        parts = line.split()
        qubits = parts[1:]
        new_line = "H " + " ".join(qubits)
        new_lines.append(new_line)
    else:
        new_lines.append(line)

final_content = "\n".join(new_lines)

with open(output_path, 'w') as f:
    f.write(final_content)

print(f"Cleaned circuit saved to {output_path}")
