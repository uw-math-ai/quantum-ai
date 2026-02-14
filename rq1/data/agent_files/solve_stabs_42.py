import stim
import numpy as np

def solve():
    stabilizers = [
        "IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX",
        "IXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXX",
        "XXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXI",
        "IIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZ",
        "IZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ",
        "ZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZI",
        "XXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIII",
        "ZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIII"
    ]
    
    num_qubits = 42
    stabs = [stim.PauliString(s) for s in stabilizers]
    
    # Check commutativity
    for i in range(len(stabs)):
        for j in range(i+1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                print(f"Anticommutes: {i}, {j}")
                return

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
    
    # We will incrementally try to find stabilizers that complete the set
    # We can iterate through all possible Pauli strings? No, too large.
    # We should use the null space method.
    
    # Basis of the stabilizer group
    current_rows = np.array([to_binary(s) for s in stabs], dtype=np.uint8)
    
    # 1. Find the centralizer (Paulis that commute with all current stabs)
    # Solve H @ J @ x = 0
    # H is (38 x 84)
    # J is (84 x 84)
    # A = H @ J is (38 x 84)
    
    J = np.zeros((2*num_qubits, 2*num_qubits), dtype=np.uint8)
    for k in range(num_qubits):
        J[k, k+num_qubits] = 1
        J[k+num_qubits, k] = 1
        
    A = (current_rows @ J) % 2
    
    # Gaussian elimination to find null space basis
    # We want x such that A x = 0.
    
    # Transpose A to solve A x = 0 -> x^T A^T = 0
    # Or just use standard null space finding.
    
    rows, cols = A.shape
    mat = A.copy()
    
    pivots = []
    pivot_row = 0
    pivot_col_to_row = {}
    
    # RREF
    for c in range(cols):
        if pivot_row >= rows: break
        swap = -1
        for r in range(pivot_row, rows):
            if mat[r, c] == 1:
                swap = r
                break
        if swap != -1:
            mat[[pivot_row, swap]] = mat[[swap, pivot_row]]
            # Eliminate
            for r in range(rows):
                if r != pivot_row and mat[r, c] == 1:
                    mat[r] ^= mat[pivot_row]
            pivot_col_to_row[c] = pivot_row
            pivots.append(c)
            pivot_row += 1
            
    # Free variables
    free_vars = [c for c in range(cols) if c not in pivots]
    
    null_basis = []
    for free in free_vars:
        # Set free variable to 1, others to 0, solve for pivot variables
        vec = np.zeros(cols, dtype=np.uint8)
        vec[free] = 1
        
        # Back substitution for pivot variables
        # For each pivot p, the equation is vec[p] + sum(mat[r, k]*vec[k]) = 0
        # where r is the row for pivot p.
        for p in reversed(pivots):
            r = pivot_col_to_row[p]
            val = 0
            for k in range(p+1, cols):
                if mat[r, k]: val ^= vec[k]
            vec[p] = val
        null_basis.append(vec)
        
    candidates = [from_binary(v) for v in null_basis]
    
    # Now pick candidates to complete the set
    
    # Helper to calculate rank of a set of binary vectors
    def matrix_rank(matrix):
        if len(matrix) == 0: return 0
        m = matrix.copy()
        pr = 0
        rs, cs = m.shape
        for c in range(cs):
            if pr >= rs: break
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

    current_rank = matrix_rank(current_rows)
    print(f"Current rank: {current_rank}")
    
    for cand in candidates:
        if len(final_stabs) == 42: break
        
        # Must commute with stabilizers added in this loop (it already commutes with original 38)
        commutes = True
        for i in range(38, len(final_stabs)):
            if not cand.commutes(final_stabs[i]):
                commutes = False
                break
        if not commutes: continue
        
        # Must be independent
        # Check if rank increases
        new_mat = np.vstack([current_rows, to_binary(cand)])
        new_rank = matrix_rank(new_mat)
        
        if new_rank > current_rank:
            final_stabs.append(cand)
            current_rows = new_mat
            current_rank = new_rank
            print(f"Added stabilizer: {cand}")
            
    if len(final_stabs) != 42:
        print(f"Failed: only have {len(final_stabs)} stabilizers")
        # Just generate what we have? 
        # stim.Tableau.from_stabilizers requires n stabilizers for n qubits.
        return

    # Generate circuit
    t = stim.Tableau.from_stabilizers(final_stabs)
    c = t.to_circuit("elimination")
    
    with open("circuit_attempt_42.stim", "w") as f:
        f.write(str(c))
    print("Success")

if __name__ == "__main__":
    solve()
