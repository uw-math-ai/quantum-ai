
with open('target_stabilizers.txt', 'r') as f:
    lines = f.readlines()
    print(f"Number of lines: {len(lines)}")
    if lines:
        print(f"Length of first line: {len(lines[0].strip())}")

import stim
c = stim.Circuit.from_file('candidate_graph.stim')
print(f"Original circuit num qubits: {c.num_qubits}")

# Replace RX with H (assuming input is |0>)
new_c = stim.Circuit()
for instruction in c:
    if instruction.name == "RX":
        # RX resets to |+>. If input is |0>, H does the same.
        # But RX also resets. If we are not allowed to reset, and input is |0>, we use H.
        targets = instruction.targets_copy()
        new_c.append("H", targets)
    else:
        new_c.append(instruction)

print(f"New circuit num qubits: {new_c.num_qubits}")

with open('candidate_graph_fixed.stim', 'w') as f:
    f.write(str(new_c))
