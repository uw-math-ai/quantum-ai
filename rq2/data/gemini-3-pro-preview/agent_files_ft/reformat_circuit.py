
import re

with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate_ft_anpaz.stim', 'r') as f:
    content = f.read()

# Replace newlines with spaces to parse tokens
tokens = content.replace('\n', ' ').split()

# Reconstruct with safe line breaks
# Logic: Start new line for each Gate
output = []
current_line = []

# Stim gates: CX, H, M, R, etc.
gates = {'CX', 'H', 'M', 'R', 'RX', 'RY', 'RZ', 'MX', 'MY', 'MZ', 'MPP', 'DETECTOR', 'OBSERVABLE_INCLUDE', 'SHIFT_COORDS', 'TICK', 'QUBIT_COORDS'}

for token in tokens:
    if token in gates:
        if current_line:
            output.append(" ".join(current_line))
            current_line = []
        current_line.append(token)
    else:
        current_line.append(token)

if current_line:
    output.append(" ".join(current_line))

print("\n".join(output))
