import stim

# Read the original circuit from the task
circuit_text = """H 0
S 111 178
H 3 5 6 12 29 77 79 80 86 103
CX 0 3 0 5 0 6 0 12 0 29 0 77 0 79 0 80 0 86 0 103 0 111 0 171 0 173 0 178
H 74 153 155 160
CX 74 0 153 0 155 0 160 0 178 1 1 178 178 1
H 1
S 1
CX 1 171 1 173
S 37
H 3 5 6 12 29 37 74 77 79 80 86 103 171 173
CX 3 1 5 1 6 1 12 1 29 1 37 1 74 1 77 1 79 1 80 1 86 1 103 1 153 1 155 1 160 1 171 1 173 1 37 2 2 37 37 2
H 2
S 2
H 74
CX 74 2 153 2 155 2 160 2 111 3 3 111 111 3
S 3
H 3
S 3 74
CX 3 74 153 3 155 3 160 3 74 4 4 74 74 4
S 4
H 4
CX 153 4 155 4 160 4 178 5 5 178 178 5
H 5"""

# Parse to count unique qubits
lines = circuit_text.strip().split('\n')
qubits = set()
for line in lines:
    parts = line.split()
    if len(parts) > 1:
        gate = parts[0]
        if gate in ['CX', 'CZ']:
            for i in range(1, len(parts), 2):
                qubits.add(int(parts[i]))
                qubits.add(int(parts[i+1]))
        else:
            for p in parts[1:]:
                qubits.add(int(p))

print(f"Qubits in partial circuit: {sorted(qubits)[:20]}... (total: {len(qubits)})")
print(f"Max qubit: {max(qubits)}")
