import stim
import numpy as np

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
    "ZZZZZZZZZZZZZZZZZZZZ"
]

num_qubits = 20
num_stabilizers = len(stabilizers)

print(f"Number of stabilizers: {num_stabilizers}")
print(f"Number of qubits: {num_qubits}")

# Check lengths
for i, s in enumerate(stabilizers):
    if len(s) != num_qubits:
        print(f"Error: Stabilizer {i} has length {len(s)}")

# Parse to binary matrix
xs = np.zeros((num_stabilizers, num_qubits), dtype=int)
zs = np.zeros((num_stabilizers, num_qubits), dtype=int)

for r, s in enumerate(stabilizers):
    for c, char in enumerate(s):
        if char == 'X':
            xs[r, c] = 1
        elif char == 'Z':
            zs[r, c] = 1
        elif char == 'Y':
            xs[r, c] = 1
            zs[r, c] = 1

# Check commutation
commutes = True
for i in range(num_stabilizers):
    for j in range(i + 1, num_stabilizers):
        val = np.sum(xs[i] * zs[j] + zs[i] * xs[j])
        if val % 2 != 0:
            print(f"Stabilizers {i} and {j} anticommute!")
            commutes = False

if commutes:
    print("All stabilizers commute.")
else:
    print("Some stabilizers anticommute.")

# Check independence using Gaussian elimination
# Form a (num_stabilizers x 2*num_qubits) matrix
check_matrix = np.concatenate((xs, zs), axis=1)

# Gaussian elimination over GF(2)
# We want to find the rank.
def rank_gf2(mat):
    mat = mat.copy()
    rows, cols = mat.shape
    pivot_row = 0
    for col in range(cols):
        if pivot_row >= rows:
            break
        # Find a row with a 1 in this column
        swap_row = -1
        for r in range(pivot_row, rows):
            if mat[r, col] == 1:
                swap_row = r
                break
        
        if swap_row == -1:
            continue
            
        mat[[pivot_row, swap_row]] = mat[[swap_row, pivot_row]]
        
        # Eliminate other rows
        for r in range(rows):
            if r != pivot_row and mat[r, col] == 1:
                mat[r] ^= mat[pivot_row]
        pivot_row += 1
    return pivot_row

r = rank_gf2(check_matrix)
print(f"Rank of stabilizer matrix: {r}")

if r < num_stabilizers:
    print("Stabilizers are linearly dependent.")
elif r == num_stabilizers:
    print("Stabilizers are linearly independent.")

# Try to complete the stabilizer set to 20
if commutes and r == num_stabilizers:
    # We need 20 - r more stabilizers
    # We can try adding Z on free qubits
    pass

# We can output the tableau using Stim if we can form a full set.
# Let's try to find a full set.
try:
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True)
    print("Successfully created a tableau (underconstrained).")
    # This tableau defines a valid state.
    # We can use it to generate a circuit.
    circuit = t.to_circuit()
    print("Generated circuit:")
    print(circuit)
    
except Exception as e:
    print(f"Failed to create tableau: {e}")

