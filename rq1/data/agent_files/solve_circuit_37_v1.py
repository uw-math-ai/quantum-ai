import stim
import numpy as np
import random

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
        # I is 0, 0
    return x, z

n_qubits = 37

# Build check matrix
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

comm_matrix = (M @ Omega) % 2

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

def is_independent(M, v):
    aug = np.vstack([M, v])
    return rank_gf2(aug) > rank_gf2(M)

# Find 37th stabilizer
found_v = None
found_s = None

# Try simple Pauli strings first (weight 1, 2, etc.)
# But since we just need ONE, random is fine.
for _ in range(5000):
    # Generate random x, z
    vx = np.random.randint(0, 2, n_qubits, dtype=np.uint8)
    vz = np.random.randint(0, 2, n_qubits, dtype=np.uint8)
    v = np.concatenate([vx, vz])
    
    # Check commutation
    # v @ Omega @ M^T = 0
    # Actually checking if v commutes with all rows of M
    # (v @ Omega @ M.T) % 2
    res = (v @ Omega @ M.T) % 2
    if np.all(res == 0):
        if is_independent(M, v):
            found_v = v
            # Convert to string
            s_new = ""
            for i in range(n_qubits):
                if vx[i] == 0 and vz[i] == 0: s_new += "I"
                elif vx[i] == 1 and vz[i] == 0: s_new += "X"
                elif vx[i] == 0 and vz[i] == 1: s_new += "Z"
                elif vx[i] == 1 and vz[i] == 1: s_new += "Y"
            found_s = s_new
            print(f"Found 37th stabilizer: {s_new}")
            break

if found_s is None:
    print("Could not find 37th stabilizer.")
    exit(1)

all_stabilizers = stabilizers + [found_s]
try:
    # Convert strings to PauliString objects
    paulis = [stim.PauliString(s) for s in all_stabilizers]
    
    # Create Tableau from stabilizers
    # Note: from_stabilizers returns a tableau T such that T(Z_k) = S_k (up to signs?)
    # If allow_redundant=False (default), it expects exactly n independent stabilizers.
    t = stim.Tableau.from_stabilizers(paulis)
    
    # Generate circuit
    # The tableau T maps Z basis to the stabilizer basis.
    # So the circuit for T maps |0> to the stabilizer state.
    # We can get the circuit using `to_circuit`.
    c = t.to_circuit(method="elimination")
    
    # Write to file
    with open("circuit_solution.stim", "w") as f:
        f.write(str(c))
        
    print("Circuit generated in circuit_solution.stim")
    
except Exception as e:
    print(f"Error in stim: {e}")
    exit(1)
