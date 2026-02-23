
import stim
import sys
import os

# Add the directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files'))

# Read fixed generators
with open(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files', 'stabilizers_175_fixed.txt'), 'r') as f:
    generators_str = [line.strip() for line in f]

generators = [stim.PauliString(g) for g in generators_str]
print(f"Loaded {len(generators)} generators")

def get_stabilizer_matrix(pauli_strings):
    n = len(pauli_strings[0])
    # Build constraint matrix M such that M * v = 0 means v commutes with all stabilizers
    # v is a vector of length 2n (x1..xn, z1..zn)
    # The condition for commuting with g = (z_g, x_g) is:
    # sum_k (x_v_k * z_g_k + z_v_k * x_g_k) = 0
    # So the row for g has:
    # - z_g_k at position corresponding to x_v_k (indices 0..n-1)
    # - x_g_k at position corresponding to z_v_k (indices n..2n-1)
    
    mat = []
    for p in pauli_strings:
        row = []
        # First n cols: coeff of x_v_k -> z_g_k
        for k in range(n):
            row.append(p[k] in [2, 3]) # Y or Z has Z component
        # Next n cols: coeff of z_v_k -> x_g_k
        for k in range(n):
            row.append(p[k] in [1, 2]) # X or Y has X component
        mat.append(row)
    return mat

def solve_nullspace(mat, n_vars):
    # Gaussian elimination to find nullspace basis
    # mat is m x n_vars
    # We want to find basis for kernel.
    # Augmented matrix [M | I] is useful?
    # Or just standard method.
    
    # Work with transpose to find kernel?
    # Kernel of M is orthogonal complement of RowSpace(M).
    # M has 174 rows, 350 cols.
    # We reduce M to RREF.
    
    rows = len(mat)
    cols = n_vars
    
    # Make copy
    m = [row[:] for row in mat]
    
    pivot_cols = []
    pivot_row = 0
    
    for col in range(cols):
        if pivot_row >= rows:
            break
            
        pivot = -1
        for r in range(pivot_row, rows):
            if m[r][col]:
                pivot = r
                break
        
        if pivot == -1:
            continue
            
        m[pivot_row], m[pivot] = m[pivot], m[pivot_row]
        pivot_cols.append(col)
        
        for r in range(rows):
            if r != pivot_row and m[r][col]:
                for c in range(col, cols):
                    m[r][c] ^= m[pivot_row][c]
        
        pivot_row += 1
    
    rank = pivot_row
    print(f"Rank of constraint matrix: {rank}")
    
    # Back substitution to find nullspace basis
    # Free variables correspond to cols not in pivot_cols
    free_vars = [c for c in range(cols) if c not in pivot_cols]
    
    basis = []
    for free_var in free_vars:
        # Construct solution vector v
        # v[free_var] = 1, other free vars = 0
        v = [0] * cols
        v[free_var] = 1
        
        # Determine pivot vars
        # From bottom up
        for r in range(rank - 1, -1, -1):
            pivot_col = pivot_cols[r]
            val = 0
            for c in range(pivot_col + 1, cols):
                if m[r][c]:
                    val ^= v[c]
            v[pivot_col] = val
        basis.append(v)
        
    return basis

mat = get_stabilizer_matrix(generators)
nullspace = solve_nullspace(mat, 350)
print(f"Nullspace dimension: {len(nullspace)}")

# The nullspace contains the stabilizers themselves (because they commute with each other)
# AND the logical operators.
# We need to find one vector in nullspace that is NOT in the span of the stabilizers.
# The span of stabilizers corresponds to the row space of the CHECK matrix?
# No, stabilizers correspond to vectors (x_g, z_g).
# In our constraint matrix construction:
# v = (x_v, z_v).
# g = (x_g, z_g).
# The row was (z_g, x_g).
# The stabilizers themselves are solutions because for any h in S, h commutes with all g in S.
# So (x_h, z_h) is a solution.
# Wait, my matrix row was (z_g, x_g).
# The solution v is (x_v, z_v).
# If h is a stabilizer, v = (x_h, z_h).
# Commutativity check: sum (x_h * z_g + z_h * x_g) = 0.
# This is exactly the symplectic product.
# Since stabilizers commute, they are in the nullspace.

# So `nullspace` contains vectors corresponding to stabilizers + logicals.
# We need to filter out the stabilizers.
# We can just iterate through `nullspace` basis vectors, convert them to PauliStrings,
# and check if they are independent of `generators`.

def vec_to_pauli(v, n=175):
    # v is (x1..xn, z1..zn)
    s = ""
    for k in range(n):
        x = v[k]
        z = v[n+k]
        if x and z:
            s += "Y"
        elif x:
            s += "X"
        elif z:
            s += "Z"
        else:
            s += "I"
    return stim.PauliString(s)

def check_independence(gens, candidate):
    # Gaussian elimination to check if candidate is in span of gens
    # Represent gens as matrix of (x, z)
    # Append candidate
    # Check rank
    
    n = 175
    mat = []
    for p in gens + [candidate]:
        row = []
        for k in range(n):
            row.append(p[k] in [1, 2]) # X
            row.append(p[k] in [2, 3]) # Z
        mat.append(row)
        
    # Standard Gaussian elimination
    rows = len(mat)
    cols = 2 * n
    pivot_row = 0
    for col in range(cols):
        if pivot_row >= rows:
            break
        pivot = -1
        for r in range(pivot_row, rows):
            if mat[r][col]:
                pivot = r
                break
        if pivot == -1:
            continue
        mat[pivot_row], mat[pivot] = mat[pivot], mat[pivot_row]
        for r in range(rows):
            if r != pivot_row and mat[r][col]:
                for c in range(col, cols):
                    mat[r][c] ^= mat[pivot_row][c]
        pivot_row += 1
        
    return pivot_row == len(gens) + 1

# Try to find independent generator
for vec in nullspace:
    cand = vec_to_pauli(vec)
    if check_independence(generators, cand):
        print(f"Found independent logical operator: {cand}")
        
        # Generate circuit
        final_gens = generators + [cand]
        try:
            tableau = stim.Tableau.from_stabilizers(final_gens)
            circuit = tableau.to_circuit(method="elimination")
            print("Circuit generated successfully")
            with open(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files', 'circuit_175.stim'), 'w') as f:
                f.write(str(circuit))
            sys.exit(0)
        except Exception as e:
            print(f"Error generating tableau: {e}")
            
print("Could not find independent generator from nullspace basis.")
