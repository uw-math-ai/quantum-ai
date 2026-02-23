import re

with open("circuit_25_qubits.stim", "r") as f:
    content = f.read()

# Find all integers in the file
integers = [int(x) for x in re.findall(r'\b\d+\b', content)]
max_qubit = max(integers) if integers else 0
print(f"Max qubit index found: {max_qubit}")
