import stim
import numpy as np

def solve():
    stabilizers = [
        "XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI",
        "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX",
        "IIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXX",
        "ZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZI",
        "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
        "IIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
        "XXXIIIIXXXIIIIXXXIIIIXXXIIIIXXXIIIIXXXIIII",
        "ZZZIIIIZZZIIIIZZZIIIIZZZIIIIZZZIIIIZZZIIII"
    ]
    
    num_qubits = 42
    stabs = [stim.PauliString(s) for s in stabilizers]
    
    # Check commutativity
    for i in range(len(stabs)):
        for j in range(i+1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                print(f"Anticommutes: {i}, {j}")
                # return

    # Helper to convert to binary vector
    def to_binary(p):
        row = np.zeros(2*num_qubits, dtype=np.uint8)
        for k in range(num_qubits):
            # p[k] returns 0=I, 1=X, 2=Y, 3=Z
            val = p[k]
            if val == 1 or val == 2: row[k] = 1 # X component
            if val == 3 or val == 2: row[k + num_qubits] = 1 # Z component
        return row

    def from_binary(row):
        s = ""
        for k in range(num_qubits):
            x = row[k]
            z = row[k + num_qubits]
            if x and z: s += "Y"
            elif x: s += "X"
            elif z: s += "Z"
            else: s += "I"
        return stim.PauliString(s)
        
    final_stabs = list(stabs)
    
    # Check linear independence (rank)
    current_rows = np.array([to_binary(s) for s in stabs], dtype=np.uint8)

    # Helper to calculate rank of a set of binary vectors (Gaussian elimination)
    def matrix_rank(matrix):
        if len(matrix) == 0: return 0
        m = matrix.copy()
        rs, cs = m.shape
        pr = 0
        for c in range(cs):
            if pr >= rs: break
            # Find pivot
            sw = -1
            for r in range(pr, rs):
                if m[r, c] == 1:
                    sw = r
                    break
            if sw != -1:
                m[[pr, sw]] = m[[sw, pr]]
                for r in range(rs):
                    if r != pr and m[r, c] == 1:
                        m[r] ^= m[pr]
                pr += 1
        return pr

    rank = matrix_rank(current_rows)
    print(f"Initial rank: {rank}")
    
    # We need 42 - 38 = 4 more stabilizers to complete the set
    
    # Find candidates that commute with all current stabilizers
    # Construct commutation matrix check
    # A x = 0
    # where A = stabilizers_matrix @ J
    
    J = np.zeros((2*num_qubits, 2*num_qubits), dtype=np.uint8)
    for k in range(num_qubits):
        J[k, k+num_qubits] = 1
        J[k+num_qubits, k] = 1
        
    A = (current_rows @ J) % 2
    
    # Find null space of A
    # A is (38 x 84)
    # Null space dimension >= 84 - 38 = 46.
    
    # Using scipy or custom Gaussian elimination for null space
    # Let's use custom RREF again to find basis for null space
    
    rows, cols = A.shape
    mat = A.copy()
    pivots = []
    pivot_row = 0
    pivot_col_to_row = {}
    
    for c in range(cols):
        if pivot_row >= rows: break
        swap = -1
        for r in range(pivot_row, rows):
            if mat[r, c] == 1:
                swap = r
                break
        if swap != -1:
            mat[[pivot_row, swap]] = mat[[swap, pivot_row]]
            for r in range(rows):
                if r != pivot_row and mat[r, c] == 1:
                    mat[r] ^= mat[pivot_row]
            pivot_col_to_row[c] = pivot_row
            pivots.append(c)
            pivot_row += 1
            
    free_vars = [c for c in range(cols) if c not in pivots]
    
    null_basis = []
    for free in free_vars:
        vec = np.zeros(cols, dtype=np.uint8)
        vec[free] = 1
        for p in reversed(pivots):
            r = pivot_col_to_row[p]
            val = 0
            for k in range(p+1, cols):
                if mat[r, k]: val ^= vec[k]
            vec[p] = val
        null_basis.append(vec)
        
    candidates = [from_binary(v) for v in null_basis]
    print(f"Found {len(candidates)} candidates in the centralizer")
    
    # Greedily add independent commuting stabilizers
    added_count = 0
    
    # Re-calculate rank with updated rows
    current_mat = current_rows.copy()
    current_rank = rank

    for cand in candidates:
        if len(final_stabs) == 42: break
        
        # Check if it commutes with ALREADY ADDED new stabilizers
        # (It commutes with original ones by definition of null space)
        commutes = True
        for i in range(38, len(final_stabs)):
            if not cand.commutes(final_stabs[i]):
                commutes = False
                break
        if not commutes: continue
        
        # Check independence
        cand_vec = to_binary(cand)
        test_mat = np.vstack([current_mat, cand_vec])
        new_rank = matrix_rank(test_mat)
        
        if new_rank > current_rank:
            final_stabs.append(cand)
            current_mat = test_mat
            current_rank = new_rank
            print(f"Added: {cand}")
            added_count += 1
            
    if len(final_stabs) == 42:
        print("Successfully found full set of stabilizers")
        # Generate circuit
        t = stim.Tableau.from_stabilizers(final_stabs)
        c = t.to_circuit("elimination")
        with open("circuit_attempt_42_v2.stim", "w") as f:
            f.write(str(c))
    else:
        print(f"Failed to complete set. Only {len(final_stabs)} stabilizers.")

if __name__ == "__main__":
    solve()
