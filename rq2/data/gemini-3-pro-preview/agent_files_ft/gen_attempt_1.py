import sys
import stim

# Inputs
input_circuit_str = """CX 1 0 0 1 1 0
H 0
CX 0 2 0 3 0 8
H 1
CX 1 0 2 1 1 2 2 1 2 1 3 2 2 3 3 2 3 2 3 4 3 5 7 6 6 7 7 6 6 7 8 6 8 7"""

stabilizers = [
    "XXXXXXIII", "XXXIIIXXX", 
    "ZZIIIIIII", "ZIZIIIIII", 
    "IIIZZIIII", "IIIZIZIII", 
    "IIIIIIZZI", "IIIIIIZIZ"
]
distance = 3
data_qubits = list(range(9))
flag_qubits = list(range(9, 17)) # 8 flags

def format_circuit(c_str):
    lines = c_str.strip().split('\n')
    formatted = []
    for line in lines:
        parts = line.split()
        if not parts: continue
        gate = parts[0]
        targets = [int(x) for x in parts[1:]]
        formatted.append(f"{gate} {' '.join(str(t) for t in targets)}")
    return "\n".join(formatted)

base = format_circuit(input_circuit_str)

# Build checks
num_rounds = 2
checks = []
ancilla_idx = 9

for round in range(num_rounds):
    # Stabilizer 0: XXXXXXIII (0-5)
    checks.append(f"H {ancilla_idx}")
    for q in [0, 1, 2, 3, 4, 5]:
        checks.append(f"CX {ancilla_idx} {q}")
    checks.append(f"H {ancilla_idx}")
    checks.append(f"M {ancilla_idx}") 
    ancilla_idx += 1

    # Stabilizer 1: XXXIIIXXX (0-2, 6-8)
    checks.append(f"H {ancilla_idx}")
    for q in [0, 1, 2, 6, 7, 8]:
        checks.append(f"CX {ancilla_idx} {q}")
    checks.append(f"H {ancilla_idx}")
    checks.append(f"M {ancilla_idx}")
    ancilla_idx += 1

    # Stabilizer 2: ZZIIIIIII (0,1)
    checks.append(f"CX 0 {ancilla_idx} 1 {ancilla_idx}")
    checks.append(f"M {ancilla_idx}")
    ancilla_idx += 1

    # Stabilizer 3: ZIZIIIIII (0,2)
    checks.append(f"CX 0 {ancilla_idx} 2 {ancilla_idx}")
    checks.append(f"M {ancilla_idx}")
    ancilla_idx += 1

    # Stabilizer 4: IIIZZIIII (3,4)
    checks.append(f"CX 3 {ancilla_idx} 4 {ancilla_idx}")
    checks.append(f"M {ancilla_idx}")
    ancilla_idx += 1

    # Stabilizer 5: IIIZIZIII (3,5)
    checks.append(f"CX 3 {ancilla_idx} 5 {ancilla_idx}")
    checks.append(f"M {ancilla_idx}")
    ancilla_idx += 1

    # Stabilizer 6: IIIIIIZZI (6,7)
    checks.append(f"CX 6 {ancilla_idx} 7 {ancilla_idx}")
    checks.append(f"M {ancilla_idx}")
    ancilla_idx += 1

    # Stabilizer 7: IIIIIIZIZ (6,8)
    checks.append(f"CX 6 {ancilla_idx} 8 {ancilla_idx}")
    checks.append(f"M {ancilla_idx}")
    ancilla_idx += 1

full_circuit = base + "\n" + "\n".join(checks)
print(full_circuit)
