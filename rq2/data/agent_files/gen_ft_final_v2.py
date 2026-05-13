import stim

# Original circuit
base = """H 0 1 3
CX 0 1 0 3 0 6 0 8 6 1 1 6 6 1 1 5
H 2
CX 2 5 3 4 6 4 4 6 6 4 4 5 4 6 4 8 7 6 8 6 8 7"""

c = stim.Circuit(base)

# Stabilizers
# (Type, Indices)
stabilizers = [
    ("X", [0, 1, 3, 4]),
    ("X", [4, 5, 7, 8]),
    ("X", [2, 5, 8]),
    ("X", [3, 6, 8]),
    ("Z", [3, 4, 6, 7]),
    ("Z", [1, 2, 4, 5]),
    ("Z", [0, 1]),
    ("Z", [7, 8])
]

# Add checks
ancilla_start = 9

for i, (stype, qubits) in enumerate(stabilizers):
    anc = ancilla_start + i
    
    if stype == "X":
        # H ancilla
        c.append("H", [anc])
        # CX ancilla -> data
        for q in qubits:
            c.append("CX", [anc, q])
        # H ancilla
        c.append("H", [anc])
        # Measure
        c.append("M", [anc])
        
    elif stype == "Z":
        # CX data -> ancilla
        for q in qubits:
            c.append("CX", [q, anc])
        # Measure
        c.append("M", [anc])
        
print(c)
