import stim
import numpy as np

def solve_linear_system():
    raw_stabs = """
    IIXIIXIIIIIIIIIIIIIIIIIXIIXII, IIIIIIIIIIXIIXIIIIIIIXIIIIIXIII, IIIIIIIIIIIIXIIXIIIIIIIXIIIIIIX, IXIIXIIIIIIIIIIIIIIIIIIIXIXIIII, IIIIIIXXIIIIIIXIXIIIIIIIIIIIIII, IIIIIIIIXXIIIIIIIIXIXIIIIIIIIII, IIIIIIIIIIIIIIIIIIIXIIXIIXIIXII, IIIXIIIIIIXXIXIIIIIIIIIIIIIIIII, IIIIXIIIIIIIIIIIIIIIIXIIIIXXIII, IIIIIXXIIIIIXIIXXIIIIIXIIIIIXXI, IIIIIIIIXIIIIIIIIIXIIIIXIIIIIIX, XIIXIIIXIIXIIIXIIIIIIXIIXIXIIII, XIIIIIXXIIIIIIIIIIIIIIIIIIIIIXI, IXIIIIIIXXIIIIXXXIIIIIIIXIIIIIX, IIXIIIIIIIIIIIIIIXIXIIIIIXIIIII, IIZIIZIIIIIIIIIIIIIIIIIIIZIIZII, IIIIIIIIIIZIIZIIIIIIIZIIIIIZIII, IIIIIIIIIIIIZIIZIIIIIIIZIIIIIIZ, IZIIZIIIIIIIIIIIIIIIIIIIZIZIIII, IIIIIIZZIIIIIIZIZIIIIIIIIIIIIII, IIIIIIIIZZIIIIIIIIZIZIIIIIIIIII, IIIIIIIIIIIIIIIIIIIZIIZIIZIIZII, IIIZIIIIIIZZIZIIIIIIIIIIIIIIIII, IIIIZIIIIIIIIIIIIIIIIZIIIIZZIII, IIIIIZZIIIIIZIIZZIIIIIZIIIIIZZI, IIIIIIIIZIIIIIIIIIZIIIIZIIIIIIZ, ZIIZIIIZIIZIIIZIIIIIIZIIZIZIIII, ZIIIIIZZIIIIIIIIIIIIIIIIIIIIIZI, IZIIIIIIZZIIIIZZZIIIIIIIZIIIIIZ, IIZIIIIIIIIIIIIIIZIZIIIIIZIIIII
    """
    stabs = [stim.PauliString(s.strip()) for s in raw_stabs.replace('\n', '').split(',') if s.strip()]
    
    num_stabs = len(stabs)
    num_qubits = len(stabs[0])
    
    # Construct matrix A where A[j][i] = 1 if Z_i anti-commutes with Stab j
    # Z_i anti-commutes with Stab j if Stab j has X or Y at i.
    # Note: Stab j might have Z or I at i, then it commutes.
    
    matrix = []
    for j in range(num_stabs):
        row = []
        for i in range(num_qubits):
            p = stabs[j][i]
            # checking if Pauli p anti-commutes with Z
            # X and Y anti-commute with Z. I and Z commute.
            if p == 1 or p == 3: # 1=X, 2=Z, 3=Y (in stim encoding? Need to check)
                # Let's use string check to be safe
                # s[i] in 'XY'
                pass
            
            # Using stim PauliString indexing
            # 0=I, 1=X, 2=Y, 3=Z ?? No.
            # Let's just use the string repr logic
            char = str(stabs[j])[i+1] # +1 because of sign '+'
            if char in 'XY':
                row.append(1)
            else:
                row.append(0)
        matrix.append(row)
    
    A = np.array(matrix, dtype=int)
    
    # Target vector: [1, 0, ... 0]
    b = np.zeros(num_stabs, dtype=int)
    b[0] = 1
    
    # Solve A x = b over GF(2)
    # Using Gaussian elimination
    
    # Augment matrix
    aug = np.column_stack((A, b))
    rows, cols = aug.shape
    
    pivot_row = 0
    pivot_cols = []
    
    for c in range(cols - 1): # specific columns (qubits)
        if pivot_row >= rows:
            break
            
        # Find pivot
        pivot = -1
        for r in range(pivot_row, rows):
            if aug[r, c] == 1:
                pivot = r
                break
        
        if pivot != -1:
            # Swap rows
            aug[[pivot_row, pivot]] = aug[[pivot, pivot_row]]
            
            # Eliminate
            for r in range(rows):
                if r != pivot_row and aug[r, c] == 1:
                    aug[r] = (aug[r] + aug[pivot_row]) % 2
            
            pivot_cols.append(c)
            pivot_row += 1
            
    # Check if consistent
    # Check rows where LHS is all zero
    solution_found = True
    for r in range(rows):
        if np.all(aug[r, :-1] == 0) and aug[r, -1] == 1:
            print("System is inconsistent! No Z-operator solution exists.")
            solution_found = False
            break
            
    if solution_found:
        print("Solution found!")
        # Extract solution
        # Since it's underdetermined, we can set free variables to 0
        # The pivot columns correspond to variables we solve for.
        
        x = np.zeros(num_qubits, dtype=int)
        for i in range(len(pivot_cols)-1, -1, -1):
            c = pivot_cols[i]
            r = i # The row where the pivot is
            val = aug[r, -1]
            # Subtract known values (if any, but we process in reverse and only pivots matter for rref)
            # Actually in RREF, aug[r, c] is 1 and other entries in col c are 0.
            # But other entries in row r might be non-zero (free variables).
            # We set free variables to 0.
            # So x[c] = val.
            x[c] = val
            
        # Verify
        res = (A @ x) % 2
        if np.array_equal(res, b):
            print("Verified solution.")
            indices = [i for i, val in enumerate(x) if val == 1]
            print(f"Apply Z on qubits: {indices}")
        else:
            print("Verification failed.")

if __name__ == "__main__":
    solve_linear_system()
