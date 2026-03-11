import stim
import numpy as np

# Let's analyze the CZ graph structure to see if we can reduce 2-qubit gates
# The stabilizers have a clear structure - groups of 5 qubits

stabilizers = [
    "XZZXIIIIIIIIIIIIIIII",  # 0,1,2,3
    "IIIIIXZZXIIIIIIIIIII",  # 5,6,7,8
    "IIIIIIIIIIXZZXIIIIII",  # 10,11,12,13
    "IIIIIIIIIIIIIIIXZZXI",  # 15,16,17,18
    "IXZZXIIIIIIIIIIIIIII",  # 1,2,3,4
    "IIIIIIXZZXIIIIIIIIII",  # 6,7,8,9
    "IIIIIIIIIIIXZZXIIIII",  # 11,12,13,14
    "IIIIIIIIIIIIIIIIXZZX",  # 16,17,18,19
    "XIXZZIIIIIIIIIIIIIII",  # 0,2,3,4
    "IIIIIXIXZZIIIIIIIIII",  # 5,7,8,9
    "IIIIIIIIIIXIXZZIIIII",  # 10,12,13,14
    "IIIIIIIIIIIIIIIXIXZZ",  # 15,17,18,19
    "ZXIXZIIIIIIIIIIIIIII",  # 0,1,2,3,4
    "IIIIIZXIXZIIIIIIIIII",  # 5,6,7,8,9
    "IIIIIIIIIIZXIXZIIIII",  # 10,11,12,13,14
    "IIIIIIIIIIIIIIIZXIXZ",  # 15,16,17,18,19
    "XXXXXXXXXXXXXXXXXXXX",  # all
    "ZZZZZZZZZZZZZZZZZZZZ",  # all
]

# The structure suggests this is a product of smaller codes
# Qubits 0-4, 5-9, 10-14, 15-19 seem to form independent blocks
# But stabilizers 16 and 17 (global X and Z) couple them

# Let's try a manual construction approach
# Start with H on all, then add CZ based on the required correlations

# First analyze the graph structure from the CZ gates in our current solution
cz_pairs = [
    (0,2), (0,3), (0,4), (1,2), (1,3), (1,17), (1,18), (1,19),
    (2,3), (3,4), (3,17), (3,18), (3,19), (4,17), (4,18), (4,19),
    (5,6), (5,7), (5,8), (6,8), (6,17), (6,18), (6,19),
    (7,9), (7,17), (7,18), (7,19), (8,9), (9,17), (9,18), (9,19),
    (10,11), (10,14), (10,17), (10,18), (10,19),
    (11,13), (11,17), (11,18), (11,19),
    (12,13), (12,14), (12,17), (12,18), (12,19),
    (13,17), (13,18), (13,19), (14,17), (14,18), (14,19),
    (15,16), (15,17), (15,19), (16,18), (16,19), (17,19), (18,19)
]

print(f"Total CZ pairs: {len(cz_pairs)}")

# Count connections per qubit
conn_count = {}
for a, b in cz_pairs:
    conn_count[a] = conn_count.get(a, 0) + 1
    conn_count[b] = conn_count.get(b, 0) + 1

print("Connections per qubit:")
for q in sorted(conn_count.keys()):
    print(f"  q{q}: {conn_count[q]}")

# Qubits 17, 18, 19 have many connections (they're the global coupling qubits)
# This suggests we can't reduce the CZ count much without changing the structure

# Let's try the DepolarizingModel approach or other synthesis
# Check if there's redundancy we can exploit

pauli_strings = [stim.PauliString(s) for s in stabilizers]
tableau = stim.Tableau.from_stabilizers(
    pauli_strings,
    allow_redundant=True,
    allow_underconstrained=True
)

# Try different circuit methods 
for method in ['graph_state', 'elimination']:
    circ = tableau.to_circuit(method=method)
    cx = sum(len(i.targets_copy())//2 for i in circ if i.name in ['CX', 'CNOT'])
    cz = sum(len(i.targets_copy())//2 for i in circ if i.name == 'CZ')
    print(f"\n{method}: CX={cx}, CZ={cz}")
