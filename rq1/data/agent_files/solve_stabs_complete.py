import stim
import numpy as np
import sys

# Define stabilizers
stabilizers = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
]

num_qubits = 40

def stab_to_vec(s):
    # 1 if X or Y, 0 if I or Z
    vx = [1 if c in 'XY' else 0 for c in s]
    # 1 if Z or Y, 0 if I or X
    vz = [1 if c in 'ZY' else 0 for c in s]
    return np.array(vx + vz, dtype=int)

def vec_to_pauli(vec):
    n = len(vec) // 2
    s = ""
    for k in range(n):
        x = vec[k]
        z = vec[n+k]
        if x and z: s += "Y"
        elif x: s += "X"
        elif z: s += "Z"
        else: s += "I"
    return stim.PauliString(s)

def null_space(mat):
    # mat is (m, n)
    mat = mat.copy()
    m, n = mat.shape
    pivot_cols = []
    
    # Forward elimination
    r = 0
    for c in range(n):
        if r >= m: break
        if mat[r, c] == 0:
            for r2 in range(r+1, m):
                if mat[r2, c] == 1:
                    mat[[r, r2]] = mat[[r2, r]]
                    break
            else:
                continue
        for r2 in range(m):
            if r2 != r and mat[r2, c] == 1:
                mat[r2] ^= mat[r]
        pivot_cols.append(c)
        r += 1
        
    pivot_set = set(pivot_cols)
    free_vars = [c for c in range(n) if c not in pivot_set]
    
    basis = []
    for f in free_vars:
        vec = np.zeros(n, dtype=int)
        vec[f] = 1
        for r_idx, p in enumerate(pivot_cols):
            # x_p = sum(mat[r_idx, k] * x_k)
            if mat[r_idx, f] == 1:
                vec[p] = 1
        basis.append(vec)
    return basis

def is_independent(vec, basis_rows):
    if len(basis_rows) == 0: return True
    mat = np.array(basis_rows + [vec], dtype=int)
    m, n = mat.shape
    r = 0
    pivot_cols = []
    for c in range(n):
        if r >= m: break
        if mat[r, c] == 0:
            for r2 in range(r+1, m):
                if mat[r2, c] == 1:
                    mat[[r, r2]] = mat[[r2, r]]
                    break
            else:
                continue
        for r2 in range(m):
            if r2 != r and mat[r2, c] == 1:
                mat[r2] ^= mat[r]
        pivot_cols.append(c)
        r += 1
        
    # If the last row is all zeros after elimination, it was dependent.
    # But wait, we simplified the whole matrix.
    # We just check the rank.
    return r == len(basis_rows) + 1

# Start with initial stabilizers
current_vecs = [stab_to_vec(s) for s in stabilizers]
current_paulis = [stim.PauliString(s) for s in stabilizers]

print(f"Initial independent count: {len(current_vecs)}") # Assumes they are independent (checked earlier manually)

# Lambda matrix for symplectic product
n = num_qubits
Lambda = np.zeros((2*n, 2*n), dtype=int)
Lambda[0:n, n:2*n] = np.eye(n, dtype=int)
Lambda[n:2*n, 0:n] = np.eye(n, dtype=int)

while len(current_vecs) < num_qubits:
    print(f"Current count: {len(current_vecs)}. Finding next...")
    
    # M is current stabilizers matrix
    M = np.array(current_vecs)
    
    # A = M * Lambda
    A = np.dot(M, Lambda) % 2
    
    # Null space of A contains C(S)
    basis = null_space(A)
    
    # Find one vector in basis that is independent of current_vecs
    found = False
    
    # Check basis vectors directly first
    for vec in basis:
        if is_independent(vec, current_vecs):
            current_vecs.append(vec)
            p = vec_to_pauli(vec)
            current_paulis.append(p)
            print(f"Added stabilizer: {p}")
            found = True
            break
            
    if not found:
        # Try combinations of basis vectors?
        # If basis vectors are dependent on S, then their combinations are too?
        # Wait, S is a subspace of Span(basis).
        # If basis \subseteq S, then S = Span(basis) = C(S).
        # This implies S is maximal isotropic subspace.
        # So we shouldn't be here if |S| < n.
        print("Error: Could not find independent vector.")
        break

print(f"Final count: {len(current_paulis)}")

if len(current_paulis) == num_qubits:
    tableau = stim.Tableau.from_stabilizers(current_paulis)
    circuit = tableau.to_circuit()
    circuit.to_file("circuit_attempt.stim")
    print("Circuit generated.")
else:
    print("Failed to complete.")
