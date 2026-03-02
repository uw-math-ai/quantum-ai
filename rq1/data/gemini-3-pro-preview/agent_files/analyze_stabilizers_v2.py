import stim
import numpy as np
import galois

stabilizers = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXIIXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXIIXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXI",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIIXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXX",
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIIZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZI",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIIZZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
    "XXXIIIIXXXIIIIXXXIIIIXXXIIII",
    "ZZZIIIIZZZIIIIZZZIIIIZZZIIII"
]

num_qubits = 28
num_stabilizers = len(stabilizers)
print(f"Number of stabilizers: {num_stabilizers}")
print(f"Number of qubits: {num_qubits}")

# Check commutation
def anticommutes(s1, s2):
    anti = 0
    for c1, c2 in zip(s1, s2):
        if c1 != 'I' and c2 != 'I' and c1 != c2:
            anti += 1
    return anti % 2 == 1

commutes = True
for i in range(num_stabilizers):
    for j in range(i + 1, num_stabilizers):
        if anticommutes(stabilizers[i], stabilizers[j]):
            print(f"Stabilizers {i} and {j} anticommute!")
            commutes = False

if commutes:
    print("All stabilizers commute.")
else:
    print("Some stabilizers anticommute.")

# Check independence
matrix = []
for s in stabilizers:
    row = []
    # X part
    for c in s:
        row.append(1 if c in ['X', 'Y'] else 0)
    # Z part
    for c in s:
        row.append(1 if c in ['Z', 'Y'] else 0)
    matrix.append(row)

# Pad to make it a numpy array
matrix = np.array(matrix, dtype=int)
gf2_matrix = galois.GF(2)(matrix)
rank = np.linalg.matrix_rank(gf2_matrix)
print(f"Rank: {rank}")
