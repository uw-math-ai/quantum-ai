import stim
import numpy as np

stabilizers = [
    "IIIIXIIIIIXIIIXIXIXIIIIIXIIIIIIIIIIII",
    "IIIIIXIIIIIIXIIXIIIXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXIIXXIIIIIIIIIXIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIXX",
    "IIIXIIIIIIIIIIIIIIIIIIXXIIXIIXIIIIIIX",
    "XIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIXXIII",
    "IIIIIIIIIXIIIIIXIIIXIIIIIIIIXIIIIIIII",
    "XIIIIIIIIIIIIIIIXIIIIIIIXIXIIXIIXIIII",
    "IXXIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIII",
    "IXXIIIIXXIIXIIIIIIIIIIIIIIIIIIIIIIXII",
    "IIIIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXII",
    "IIIIIIIIIIXIIIIIIXXIIXIIIIIIIIIIIIIII",
    "XIIXIXXIIIIIXIIIIIIIIIIIIIIIIXIIIIIII",
    "IIXIIIIIIIIXIXIIIIIIIIIIIIIIIIXIIIIII",
    "IIIIIIIXIIIXIXIIIIIIIIXXIXIIIIIIIIIII",
    "IIIIIIIXXIIIIIXIXIIIIIIXIIXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXIIXIIXIIIIIIXXXIII",
    "IIIXIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXX",
    "IIIIZIIIIIZIIIZIZIZIIIIIZIIIIIIIIIIII",
    "IIIIIZIIIIIIZIIZIIIZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZIIZZIIIIIIIIIZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIZIIZIIIIIIIIIZZ",
    "IIIZIIIIIIIIIIIIIIIIIIZZIIZIIZIIIIIIZ",
    "ZIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIZZIII",
    "IIIIIIIIIZIIIIIZIIIZIIIIIIIIZIIIIIIII",
    "ZIIIIIIIIIIIIIIIZIIIIIIIZIZIIZIIZIIII",
    "IZZIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIIII",
    "IZZIIIIZZIIZIIIIIIIIIIIIIIIIIIIIIIZII",
    "IIIIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZII",
    "IIIIIIIIIIZIIIIIIZZIIZIIIIIIIIIIIIIII",
    "ZIIZIZZIIIIIZIIIIIIIIIIIIIIIIZIIIIIII",
    "IIZIIIIIIIIZIZIIIIIIIIIIIIIIIIZIIIIII",
    "IIIIIIIZIIIZIZIIIIIIIIZZIZIIIIIIIIIII",
    "IIIIIIIZZIIIIIZIZIIIIIIZIIZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZIIZIIZIIIIIIZZZIII",
    "IIIZIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZZ"
]

def str_to_xz(s):
    n = len(s)
    x = np.zeros(n, dtype=np.uint8)
    z = np.zeros(n, dtype=np.uint8)
    for i, c in enumerate(s):
        if c == 'X': x[i] = 1
        elif c == 'Z': z[i] = 1
        elif c == 'Y': x[i] = 1; z[i] = 1
    return x, z

n_qubits = 37
rows = []
for s in stabilizers:
    x, z = str_to_xz(s)
    rows.append(np.concatenate([x, z]))
M = np.array(rows, dtype=np.uint8)

# Symplectic form
Omega = np.zeros((2*n_qubits, 2*n_qubits), dtype=np.uint8)
for i in range(n_qubits):
    Omega[i, n_qubits+i] = 1
    Omega[n_qubits+i, i] = 1

# Check matrix C = M @ Omega
C = (M @ Omega) % 2
# We want to find basis for null space of C.
# C is 36 x 74.
# We can use Gaussian elimination to find the kernel basis.

def kernel_basis(mat):
    # Returns a list of vectors that form a basis for the kernel
    # using Gaussian elimination.
    # Transpose to solve M x = 0
    # Actually, we want x such that mat @ x = 0.
    # Standard way:
    # 1. RREF of mat.
    # 2. Identify free variables.
    # 3. Construct basis vectors.
    m = mat.copy()
    rows, cols = m.shape
    pivot_cols = []
    free_cols = []
    
    # Gaussian elimination to RREF
    pivot_row = 0
    pivots = {} # row -> col
    
    for col in range(cols):
        if pivot_row >= rows:
            free_cols.append(col)
            continue
            
        pivot = -1
        for r in range(pivot_row, rows):
            if m[r, col] == 1:
                pivot = r
                break
        
        if pivot == -1:
            free_cols.append(col)
            continue
            
        # Swap
        if pivot != pivot_row:
            m[[pivot, pivot_row]] = m[[pivot_row, pivot]]
            
        # Eliminate
        for r in range(rows):
            if r != pivot_row and m[r, col] == 1:
                m[r] ^= m[pivot_row]
        
        pivots[pivot_row] = col
        pivot_cols.append(col)
        pivot_row += 1

    # Back substitution to find basis vectors
    # For each free variable, set it to 1 and others to 0, solve for pivot variables.
    basis = []
    for free in free_cols:
        vec = np.zeros(cols, dtype=np.uint8)
        vec[free] = 1
        # Solve for pivot variables
        # For each row i from bottom to top (pivot_row-1 down to 0)
        # x[pivot_col] = sum(m[i, free_j] * x[free_j])
        # Since we are in RREF, m[i, pivot_col] = 1 and it's the only pivot in that row.
        # So x[pivot_col] = sum(m[i, c] * x[c]) where c are free columns (and other pivots to the right)
        # Actually in RREF, for row i with pivot at col p:
        # x_p + sum_{j in free} m[i, j] * x_j = 0
        # => x_p = sum_{j in free} m[i, j] * x_j
        for r in range(pivot_row):
            p = pivots[r]
            if m[r, free] == 1:
                vec[p] = 1 # +1 = -1 in GF(2)
        basis.append(vec)
        
    return basis

null_space = kernel_basis(C)
print(f"Null space dimension: {len(null_space)}")
# Expected: 74 - 36 = 38.

# Now we need to find a vector in null_space that is NOT in row_space(M).
# The row_space(M) is contained in null_space(C) because M is self-orthogonal (stabilizers commute).
# So we have 36 vectors in M that are in null_space.
# We expect dim(null_space) = 38.
# So there are 2 vectors in null_space / row_space(M).
# These correspond to logical operators X_L, Z_L (or similar).
# We just need to pick one that is independent of M.

# Check independence against M for each basis vector
def rank_gf2(mat):
    m = mat.copy()
    rows, cols = m.shape
    pivot_row = 0
    for col in range(cols):
        if pivot_row >= rows: break
        pivot = -1
        for r in range(pivot_row, rows):
            if m[r, col] == 1:
                pivot = r
                break
        if pivot == -1: continue
        if pivot != pivot_row:
            m[[pivot, pivot_row]] = m[[pivot_row, pivot]]
        for r in range(rows):
            if r != pivot_row and m[r, col] == 1:
                m[r] ^= m[pivot_row]
        pivot_row += 1
    return pivot_row

rank_M = rank_gf2(M)
print(f"Rank of M: {rank_M}")

found_v = None
found_s = None

# Try linear combinations of null space basis vectors?
# Actually, if we just check each basis vector, one of them might be independent.
# If not, a sum of them might be.
# But usually the basis vectors are enough to span the space.
for v in null_space:
    aug = np.vstack([M, v])
    if rank_gf2(aug) > rank_M:
        found_v = v
        # Convert to string
        s_new = ""
        for i in range(n_qubits):
            x = found_v[i]
            z = found_v[n_qubits+i]
            if x == 0 and z == 0: s_new += "I"
            elif x == 1 and z == 0: s_new += "X"
            elif x == 0 and z == 1: s_new += "Z"
            elif x == 1 and z == 1: s_new += "Y"
        found_s = s_new
        print(f"Found 37th stabilizer: {s_new}")
        break

if found_s is None:
    # Try random linear combinations of null space basis
    print("Trying random linear combinations of null space basis...")
    for _ in range(100):
        coeffs = np.random.randint(0, 2, len(null_space), dtype=np.uint8)
        v = np.zeros(74, dtype=np.uint8)
        for i, c in enumerate(coeffs):
            if c: v ^= null_space[i]
        
        aug = np.vstack([M, v])
        if rank_gf2(aug) > rank_M:
            found_v = v
            # Convert to string
            s_new = ""
            for i in range(n_qubits):
                x = found_v[i]
                z = found_v[n_qubits+i]
                if x == 0 and z == 0: s_new += "I"
                elif x == 1 and z == 0: s_new += "X"
                elif x == 0 and z == 1: s_new += "Z"
                elif x == 1 and z == 1: s_new += "Y"
            found_s = s_new
            print(f"Found 37th stabilizer: {s_new}")
            break

if found_s is None:
    print("Could not find 37th stabilizer.")
    exit(1)

all_stabilizers = stabilizers + [found_s]

# Generate circuit using Stim
try:
    paulis = [stim.PauliString(s) for s in all_stabilizers]
    t = stim.Tableau.from_stabilizers(paulis)
    c = t.to_circuit(method="elimination")
    
    with open("circuit_solution.stim", "w") as f:
        f.write(str(c))
    print("Circuit generated in circuit_solution.stim")
except Exception as e:
    print(f"Error in stim: {e}")
    exit(1)
