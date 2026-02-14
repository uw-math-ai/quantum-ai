import stim
import numpy as np

def solve_linear():
    stabilizers_str = [
        "XZZXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIXZZXIIIIIIIIIIIIIIII",
        "IIIIIIIIIIXZZXIIIIIIIIIII",
        "IIIIIIIIIIIIIIIXZZXIIIIII",
        "IIIIIIIIIIIIIIIIIIIIXZZXI",
        "IXZZXIIIIIIIIIIIIIIIIIIII",
        "IIIIIIXZZXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIXZZXIIIIIIIIII",
        "IIIIIIIIIIIIIIIIXZZXIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXZZX",
        "XIXZZIIIIIIIIIIIIIIIIIIII",
        "IIIIIXIXZZIIIIIIIIIIIIIII",
        "IIIIIIIIIIXIXZZIIIIIIIIII",
        "IIIIIIIIIIIIIIIXIXZZIIIII",
        "IIIIIIIIIIIIIIIIIIIIXIXZZ",
        "ZXIXZIIIIIIIIIIIIIIIIIIII",
        "IIIIIZXIXZIIIIIIIIIIIIIII",
        "IIIIIIIIIIZXIXZIIIIIIIIII",
        "IIIIIIIIIIIIIIIZXIXZIIIII",
        "IIIIIIIIIIIIIIIIIIIIZXIXZ",
        "XXXXXZZZZZZZZZZXXXXXIIIII",
        "IIIIIXXXXXZZZZZZZZZZXXXXX",
        "XXXXXIIIIIXXXXXZZZZZZZZZZ",
        "ZZZZZXXXXXIIIIIXXXXXZZZZZ"
    ]
    
    n = 25
    m = len(stabilizers_str)
    
    xs = np.zeros((m, n), dtype=int)
    zs = np.zeros((m, n), dtype=int)
    
    for i, s in enumerate(stabilizers_str):
        for j, char in enumerate(s):
            if char == 'X': xs[i, j] = 1
            elif char == 'Z': zs[i, j] = 1
            elif char == 'Y': xs[i, j] = 1; zs[i, j] = 1
            
    mat = np.concatenate([xs, zs], axis=1) # Shape (24, 50)
    
    # Check if independent
    # Gaussian elimination to find rank
    
    def get_rank_and_pivots(mat_in):
        rows_m = np.array(mat_in, dtype=int, copy=True)
        h, w = rows_m.shape
        pivots = []
        r_p = 0
        c_p = 0
        while r_p < h and c_p < w:
            if rows_m[r_p, c_p] == 0:
                swap = -1
                for k in range(r_p + 1, h):
                    if rows_m[k, c_p] == 1:
                        swap = k; break
                if swap != -1:
                    rows_m[[r_p, swap]] = rows_m[[swap, r_p]]
                else:
                    c_p += 1; continue
            
            for k in range(r_p + 1, h):
                if rows_m[k, c_p] == 1:
                    rows_m[k] ^= rows_m[r_p]
            pivots.append(c_p)
            r_p += 1
            c_p += 1
        return r_p, pivots

    rank, pivots = get_rank_and_pivots(mat)
    print(f"Rank of stabilizers: {rank}")
    
    # We need to find a vector v such that:
    # 1. v commutes with all stabilizers (v in Kernel(mat @ J))
    # 2. v is independent of stabilizers (rank([mat; v]) > rank(mat))
    
    # Symplectic form
    J = np.zeros((2*n, 2*n), dtype=int)
    J[:n, n:] = np.eye(n)
    J[n:, :n] = np.eye(n)
    
    # Commutation matrix
    C = (mat @ J) % 2
    
    # Find kernel of C
    # C is (24, 50)
    # Solve C x = 0
    # Use Gaussian elimination on C to find free variables
    
    C_rref = np.array(C, copy=True)
    pivot_cols = []
    pivot_row = 0
    col = 0
    while pivot_row < m and col < 2*n:
        if C_rref[pivot_row, col] == 0:
            swap = -1
            for r in range(pivot_row + 1, m):
                if C_rref[r, col] == 1:
                    swap = r; break
            if swap != -1:
                C_rref[[pivot_row, swap]] = C_rref[[swap, pivot_row]]
            else:
                col += 1; continue
        
        # Eliminate other rows (make it true RREF)
        for r in range(m):
            if r != pivot_row and C_rref[r, col] == 1:
                C_rref[r] ^= C_rref[pivot_row]
                
        pivot_cols.append(col)
        pivot_row += 1
        col += 1
        
    free_vars = [j for j in range(2*n) if j not in pivot_cols]
    
    # Basis for kernel
    kernel_basis = []
    for free in free_vars:
        vec = np.zeros(2*n, dtype=int)
        vec[free] = 1
        # Back substitute
        # Since RREF is diagonalized for pivots, for each pivot row `r`, pivot at `p_col`:
        # x[p_col] + sum(C[r, f] * x[f]) = 0 => x[p_col] = C[r, free]
        
        # Find which row corresponds to which pivot column
        # Since we did full elimination, each pivot column has a single 1.
        # We can map col -> row
        col_to_row = {}
        for r in range(pivot_row):
            # Find the pivot column for this row
            # It's the first non-zero entry
            p_c = -1
            for c in range(2*n):
                if C_rref[r, c] == 1:
                    p_c = c; break
            if p_c != -1:
                col_to_row[p_c] = r
                
        for p_c, r in col_to_row.items():
            if C_rref[r, free] == 1:
                vec[p_c] = 1
        
        kernel_basis.append(vec)
        
    print(f"Kernel dimension: {len(kernel_basis)}")
    
    # Check independence
    found = None
    for vec in kernel_basis:
        if get_rank_and_pivots(np.vstack([mat, vec]))[0] > rank:
            found = vec
            print("Found logical operator.")
            break
            
    if found is not None:
        # Construct Pauli string
        s_list = []
        for k in range(n):
            if found[k] and found[k+n]: s_list.append('Y')
            elif found[k]: s_list.append('X')
            elif found[k+n]: s_list.append('Z')
            else: s_list.append('I')
        s_str = "".join(s_list)
        print(f"Logical: {s_str}")
        
        full_stabilizers = stabilizers_str + [s_str]
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in full_stabilizers])
        circuit = t.to_circuit()
        with open("circuit_solution.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit generated.")

if __name__ == "__main__":
    solve_linear()
