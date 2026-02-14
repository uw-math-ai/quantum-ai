import stim
import numpy as np

stabilizers_str = [
"XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI", 
"XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX", 
"IIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXX", 
"ZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZI", 
"ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ", 
"IIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII", 
"IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZ", 
"XXXIIIIXXXIIIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIIIIIIII", 
"XXXIIIIIIIIIIIXXXIIIIIIIIIIIXXXIIIIIIIIIIIXXXIIII", 
"IIIIIIIIIIIIIIIIIIIIIXXXIIIIXXXIIIIXXXIIIIXXXIIII", 
"ZZZIIIIZZZIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIIIIIIII", 
"ZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIIIIIIIIIIZZZIIII", 
"IIIIIIIIIIIIIIIIIIIIIZZZIIIIZZZIIIIZZZIIIIZZZIIII"
]

# Find independent generators
def to_binary_row(pauli_str):
    n = len(pauli_str)
    row = np.zeros(2*n, dtype=int)
    for i, c in enumerate(pauli_str):
        if c == 'X':
            row[i] = 1
        elif c == 'Z':
            row[i+n] = 1
        elif c == 'Y':
            row[i] = 1
            row[i+n] = 1
    return row

matrix = []
for s in stabilizers_str:
    matrix.append(to_binary_row(s))

matrix = np.array(matrix, dtype=int)

# Use simple elimination to find basis indices
rows = [list(r) for r in matrix]
n_rows = len(rows)
n_cols = len(rows[0])
pivot_row = 0
basis_indices = []

temp_rows = [list(r) for r in matrix] # working copy

for col in range(n_cols):
    if pivot_row >= n_rows:
        break
    
    k = pivot_row
    while k < n_rows and temp_rows[k][col] == 0:
        k += 1
        
    if k < n_rows:
        # Found a pivot
        basis_indices.append(k) # Original index k is now at pivot_row? No.
        # We need to track which original row ends up in the basis.
        # Actually, Gaussian elimination mixes rows.
        # We want a subset of ORIGINAL rows that are independent.
        # This is equivalent to finding a basis for the ROW SPACE.
        # Standard way: Transpose and find column basis? Or just proceed carefully.
        
        # Simpler: Iterate through stabilizers, add to basis if independent of current basis.
        pass
        
        # Let's restart the basis search with the simpler approach.
        break

basis = []
basis_indices = []

for i, s_str in enumerate(stabilizers_str):
    # Check if s_str is independent of basis
    # Construct matrix of basis + s_str
    current_mat = [to_binary_row(b) for b in basis]
    candidate = to_binary_row(s_str)
    
    # Check rank
    # If rank(basis + candidate) > rank(basis), then it's independent.
    
    # Simple rank check
    mat = np.array(current_mat + [candidate])
    
    # Quick GF2 rank
    def get_rank(m):
        if len(m) == 0: return 0
        r_mat = [list(rx) for rx in m]
        nr = len(r_mat)
        nc = len(r_mat[0])
        pr = 0
        for c in range(nc):
            if pr >= nr: break
            
            p = pr
            while p < nr and r_mat[p][c] == 0:
                p += 1
            
            if p < nr:
                r_mat[pr], r_mat[p] = r_mat[p], r_mat[pr]
                for row_idx in range(nr):
                    if row_idx != pr and r_mat[row_idx][c] == 1:
                        for col_idx in range(c, nc):
                            r_mat[row_idx][col_idx] = (r_mat[row_idx][col_idx] + r_mat[pr][col_idx]) % 2
                pr += 1
        return pr

    if get_rank(mat) > len(basis):
        basis.append(s_str)
        basis_indices.append(i)

print(f"Basis size: {len(basis)}")
print(f"Basis indices: {basis_indices}")

try:
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in basis], allow_underconstrained=True)
    print("Tableau creation from basis successful.")
    
    circuit = tableau.to_circuit(method="elimination")
    print("Circuit generated successfully.")
    
    # Save to file
    with open("circuit_49.stim", "w") as f:
        f.write(str(circuit))
    print("Saved circuit to circuit_49.stim")
        
except Exception as e:
    print(f"Error: {e}")
