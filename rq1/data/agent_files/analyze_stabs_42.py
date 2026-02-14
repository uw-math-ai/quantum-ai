import stim
import numpy as np

def char_to_pauli(c):
    if c == 'I': return 0
    if c == 'X': return 1
    if c == 'Y': return 2
    if c == 'Z': return 3
    return 0

stabilizers_str = [
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

import stim
import numpy as np

def char_to_pauli(c):
    if c == 'I': return 0
    if c == 'X': return 1
    if c == 'Y': return 2
    if c == 'Z': return 3
    return 0

stabilizers_str = [
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

import stim
import numpy as np

stabilizers_str = [
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

import stim
import numpy as np

stabilizers_str = [
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

def to_binary(paulis, n):
    mat = np.zeros((len(paulis), 2*n), dtype=int)
    for i, p in enumerate(paulis):
        for k in range(n):
            if p[k] == 1 or p[k] == 2: # X or Y
                mat[i, k] = 1
            if p[k] == 3 or p[k] == 2: # Z or Y
                mat[i, k+n] = 1
    return mat

def from_binary(row, n):
    s = ""
    for k in range(n):
        x = row[k]
        z = row[k+n]
        if x == 0 and z == 0: s += "I"
        if x == 1 and z == 0: s += "X"
        if x == 0 and z == 1: s += "Z"
        if x == 1 and z == 1: s += "Y"
    return stim.PauliString(s)

def solve_completion():
    num_qubits = 42
    stabs = [stim.PauliString(s) for s in stabilizers_str]
    current_stabs = list(stabs)
    
    # We need to find 4 operators that commute with all current_stabs and are independent of them.
    # We can do this by finding the null space of the symplectic form.
    # The symplectic form is defined by matrix J = [[0, I], [I, 0]].
    # For a check matrix H (M x 2N), we want vectors v such that H J v^T = 0.
    # This gives us the centralizer C(S).
    # Since S is abelian, S \subset C(S).
    # We want to pick vectors from C(S) \ S.
    
    # Construct H
    H = to_binary(stabs, num_qubits) # 38 x 84
    
    # Construct J
    J = np.zeros((2*num_qubits, 2*num_qubits), dtype=int)
    for k in range(num_qubits):
        J[k, k+num_qubits] = 1
        J[k+num_qubits, k] = 1
        
    # We want to solve H * J * x = 0 (mod 2)
    # Let A = H * J. A is 38 x 84.
    A = (H @ J) % 2
    
    # Find null space of A
    # We can use Gaussian elimination on A to find basis for null space.
    # A x = 0
    
    # Transpose A to solve A x = 0 -> x^T A^T = 0
    # Actually, simpler to put A in RREF and identify free variables.
    
    rows, cols = A.shape
    pivot_cols = []
    free_vars = []
    
    mat = A.copy()
    pivot_row = 0
    pivots = {} # row -> col
    
    for col in range(cols):
        if pivot_row >= rows: break
        
        swap = -1
        for r in range(pivot_row, rows):
            if mat[r, col] == 1:
                swap = r
                break
        
        if swap != -1:
            mat[[pivot_row, swap]] = mat[[swap, pivot_row]]
            for r in range(rows):
                if r != pivot_row and mat[r, col] == 1:
                    mat[r] ^= mat[pivot_row]
            
            pivots[pivot_row] = col
            pivot_cols.append(col)
            pivot_row += 1
    
    rank = pivot_row
    # print(f"Rank of commutator matrix: {rank}")
    
    # Null space basis construction
    # For each free variable, set it to 1 and others to 0, determine pivot variables.
    free_cols = [c for c in range(cols) if c not in pivot_cols]
    
    null_basis = []
    
    for free in free_cols:
        vec = np.zeros(cols, dtype=int)
        vec[free] = 1
        
        # Back substitute to find pivot values
        # Since mat is in RREF (mostly), for each pivot row, mat[r, p] * x_p + sum(mat[r, free] * x_free) = 0
        # x_p = sum(mat[r, free] * x_free)
        
        for r in range(rank - 1, -1, -1):
            p = pivots[r]
            val = 0
            for c in range(p + 1, cols):
                if mat[r, c] == 1:
                    val ^= vec[c]
            vec[p] = val
            
        null_basis.append(vec)
        
    # print(f"Null space dimension: {len(null_basis)}")
    
    # The null space corresponds to the centralizer C(S).
    # It should have dimension 2N - rank(S) = 84 - 38 = 46?
    # No, wait.
    # Commutator matrix A checks commutativity with S.
    # Kernel of A is set of all Pauli strings that commute with S.
    # Since S is isotropic (commutes with itself), S is a subspace of Ker(A).
    # Dim(Ker(A)) = 2N - Rank(S) = 84 - 38 = 46.
    # S has dimension 38.
    # So C(S)/S has dimension 46 - 38 = 8.
    # This corresponds to 4 logical qubits (4 X_L and 4 Z_L).
    # We just need to pick 4 commuting operators from C(S) that are independent of S.
    # Actually, we can just pick ANY 4 commuting operators from C(S) such that {S, new} is isotropic.
    
    # Convert null basis vectors to Pauli strings
    centralizer_ops = [from_binary(v, num_qubits) for v in null_basis]
    
    # Now we need to select 4 ops from centralizer_ops that:
    # 1. Commute with each other.
    # 2. Are independent of S and each other.
    
    # Let's try to add them greedily.
    for op in centralizer_ops:
        if len(current_stabs) == 42:
            break
            
        # Check if op commutes with all current_stabs
        # By definition it commutes with original stabs.
        # But we added new ones, so we must check commutativity with new ones.
        
        commutes = True
        for s in current_stabs[38:]: # Only check against newly added
            if not s.commutes(op):
                commutes = False
                break
        
        if not commutes:
            continue
            
        # Check independence
        # We can use our rank check
        mat_check = to_binary(current_stabs + [op], num_qubits)
        
        # Simple Gaussian elimination to check rank
        def get_rank_mat(m):
            pr = 0
            rows, cols = m.shape
            tm = m.copy()
            for c in range(cols):
                if pr >= rows: break
                sw = -1
                for r in range(pr, rows):
                    if tm[r, c] == 1:
                        sw = r
                        break
                if sw != -1:
                    tm[[pr, sw]] = tm[[sw, pr]]
                    for r in range(rows):
                        if r != pr and tm[r, c] == 1:
                            tm[r] ^= tm[pr]
                    pr += 1
            return pr
            
        if get_rank_mat(mat_check) == len(current_stabs) + 1:
            current_stabs.append(op)
            print(f"Added stabilizer {len(current_stabs)}")
            
    if len(current_stabs) == 42:
        print("Found full set of stabilizers.")
        t = stim.Tableau.from_stabilizers(current_stabs)
        circ = t.to_circuit()
        with open("circuit_attempt.stim", "w") as f:
            f.write(str(circ))
        print("Circuit generated.")
    else:
        print(f"Could not complete stabilizers. Count: {len(current_stabs)}")

solve_completion()




