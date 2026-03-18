import stim

# Try different orderings and optimizations

stabilizers = [
    "XZZXIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXX",
    "ZZZZZZZZZZZZZZZZZZZZ",
]

pauli_strings = [stim.PauliString(s) for s in stabilizers]

# Find all independent stabilizers
tableau = stim.Tableau.from_stabilizers(
    pauli_strings,
    allow_redundant=True,
    allow_underconstrained=True
)

# Get the stabilizers from the tableau
print("Independent stabilizers from tableau:")
for i in range(20):
    stab = tableau.z_output(i)
    print(f"  Z{i}: {stab}")

# Try manual optimization: look at patterns
# The structure shows groups of 5 qubits with similar patterns
# Can we exploit symmetry?

# For now, let's use the best circuit we have
circuit_text = """H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
CZ 0 2 0 3 0 4 1 2 1 3 1 17 1 18 1 19 2 3 3 4 3 17 3 18 3 19 4 17 4 18 4 19 5 6 5 7 5 8 6 8 6 17 6 18 6 19 7 9 7 17 7 18 7 19 8 9 9 17 9 18 9 19 10 11 10 14 10 17 10 18 10 19 11 13 11 17 11 18 11 19 12 13 12 14 12 17 12 18 12 19 13 17 13 18 13 19 14 17 14 18 14 19 15 16 15 17 15 19 16 18 16 19 17 19 18 19
X 7 12 14 16 18
Y 2 8 9 11 19
Z 0 1 10 13 17
S 2 3 5 6 10 11 14 15 16 17
H 1 2 5 8 9 10 12 13 16 18
S 1 5 9 10 16"""

circuit = stim.Circuit(circuit_text)

# Analyze the single-qubit gate structure at the end
# Y = S H S H (or equivalent)
# Goal: merge consecutive single-qubit gates

# Let's build an optimized circuit manually
# by analyzing what single-qubit gates are applied to each qubit

single_qubit_gates = {}
for i in range(20):
    single_qubit_gates[i] = []

# Parse the gates after CZ
gates_after_cz = """X 7 12 14 16 18
Y 2 8 9 11 19
Z 0 1 10 13 17
S 2 3 5 6 10 11 14 15 16 17
H 1 2 5 8 9 10 12 13 16 18
S 1 5 9 10 16"""

for line in gates_after_cz.strip().split('\n'):
    parts = line.split()
    gate = parts[0]
    qubits = [int(q) for q in parts[1:]]
    for q in qubits:
        single_qubit_gates[q].append(gate)

print("\nSingle-qubit gates per qubit after CZ:")
for q, gates in sorted(single_qubit_gates.items()):
    if gates:
        print(f"  Qubit {q}: {' '.join(gates)}")

# Each qubit sequence:
# q0: Z
# q1: Z S H S
# q2: Y S H
# q3: S
# q5: S H S
# q6: S
# q7: X
# q8: Y H
# q9: Y H S
# q10: Z S H S
# q11: Y S
# q12: X H
# q13: Z H
# q14: X S
# q15: S
# q16: X S H S
# q17: Z S
# q18: X H
# q19: Y

# Let's simplify common patterns
# X H = SQRT_Y_DAG (or S_DAG H S_DAG)
# Z H = H X (conjugate relationship)
# etc.

# For now, the current circuit volume is 118, which is pretty good
