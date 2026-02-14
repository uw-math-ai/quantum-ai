import stim
import numpy as np

stabilizers = [
    "XXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXIXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXIXXIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIII",
    "IIIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIXXIXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIXXIXXIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXX",
    "IIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIII",
    "IIIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXII",
    "IIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZI",
    "IZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIII",
    "ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII",
    "IIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ",
    "IIXXXIIIIIIXXXIIIIIIXXXIIIIIIXXXIIII",
    "ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII"
]

def check_commutation(stabs):
    parsed = [stim.PauliString(s) for s in stabs]
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            if not parsed[i].commutes(parsed[j]):
                return False, (i, j)
    return True, None

commutes, pair = check_commutation(stabilizers)
print(f"All commute: {commutes}")
if not commutes:
    print(f"Non-commuting pair indices: {pair}")
    exit(1)

# Check independence and complete the set
def symplectic_binary_matrix(stabs):
    n = len(stabs[0])
    mat = []
    for s in stabs:
        row = []
        for char in s:
            if char in 'IX': row.append(0)
            else: row.append(1) # Z or Y has Z component
        for char in s:
            if char in 'IZ': row.append(0)
            else: row.append(1) # X or Y has X component
        mat.append(row)
    # The symplectic form is usually X|Z. But here I did Z|X. Let's stick to one convention.
    # Stim uses X then Z.
    # Let's rebuild properly:
    mat = []
    for s in stabs:
        x_part = [1 if c in 'XY' else 0 for c in s]
        z_part = [1 if c in 'ZY' else 0 for c in s]
        mat.append(x_part + z_part)
    return np.array(mat, dtype=np.uint8)

mat = symplectic_binary_matrix(stabilizers)
import galois
gf2 = galois.GF(2)
g_mat = gf2(mat)
rank = np.linalg.matrix_rank(g_mat)
print(f"Rank: {rank}")
print(f"Number of stabilizers: {len(stabilizers)}")

# If rank < 36, we need to add stabilizers.
# We can find the null space of the matrix in the symplectic inner product to find logical operators, 
# then pick commuting ones to complete the stabilizer group.

# Construct a Tableau
# We can try to just use stim.Tableau.from_stabilizers but it requires N stabilizers for N qubits?
# Let's check.
try:
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    print("Tableau creation successful (underconstrained allowed).")
    
    # Generate circuit
    circ = t.to_circuit()
    print("Circuit generated.")
    
    with open("circuit_36_v4.stim", "w") as f:
        f.write(str(circ))
        
except Exception as e:
    print(f"Error: {e}")

