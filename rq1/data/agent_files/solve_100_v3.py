import stim
import numpy as np

def to_check_matrix(stabs, n):
    mat = np.zeros((len(stabs), 2*n), dtype=int)
    for i, s in enumerate(stabs):
        for k in range(n):
            if k < len(s):
                p = 0
                c = s[k]
                if c == 'X': p = 1
                elif c == 'Z': p = 3
                elif c == 'Y': p = 2
                
                if p == 1 or p == 2: # X or Y
                    mat[i, k] = 1
                if p == 3 or p == 2: # Z or Y
                    mat[i, k + n] = 1
    return mat

def get_rank_GF2(mat):
    # Use standard Gaussian elimination over GF(2)
    m = mat.copy()
    rows, cols = m.shape
    pivot_row = 0
    for j in range(cols):
        if pivot_row >= rows: break
        
        # Find pivot in current column j, starting from pivot_row
        pivot = -1
        for i in range(pivot_row, rows):
            if m[i, j]:
                pivot = i
                break
        
        if pivot == -1: continue
        
        # Swap rows
        if pivot != pivot_row:
            temp = m[pivot_row].copy()
            m[pivot_row] = m[pivot]
            m[pivot] = temp
            
        # Eliminate entries in this column for all other rows
        for i in range(rows):
            if i != pivot_row and m[i, j]:
                m[i] ^= m[pivot_row]
                
        pivot_row += 1
        
    return pivot_row

def find_null_space(mat):
    # Find basis for null space of mat * x = 0 over GF(2)
    m = mat.copy()
    rows, cols = m.shape
    
    # Gaussian elimination to RREF
    p_row = 0
    pivots = []
    
    for j in range(cols):
        if p_row >= rows: break
        pivot = -1
        for i in range(p_row, rows):
            if m[i, j]:
                pivot = i
                break
        if pivot == -1: continue
        
        # Swap
        if pivot != p_row:
            temp = m[p_row].copy()
            m[p_row] = m[pivot]
            m[pivot] = temp
            
        # Eliminate
        for i in range(rows):
            if i != p_row and m[i, j]:
                m[i] ^= m[p_row]
                
        pivots.append((p_row, j))
        p_row += 1
        
    pivot_cols = set(c for r, c in pivots)
    free_vars = [j for j in range(cols) if j not in pivot_cols]
    
    basis = []
    for free in free_vars:
        vec = np.zeros(cols, dtype=int)
        vec[free] = 1
        # Back substitute
        for r, c in reversed(pivots):
            val = 0
            for k in range(c + 1, cols):
                if m[r, k]:
                    val ^= vec[k]
            vec[c] = val
        basis.append(vec)
        
    return basis

def vec_to_pauli(vec, n):
    s = ""
    for i in range(n):
        x = vec[i]
        z = vec[i+n]
        if x and z: s += "Y"
        elif x: s += "X"
        elif z: s += "Z"
        else: s += "I"
    return str(stim.PauliString(s))

def main():
    try:
        with open("stabilizers_100.txt", "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        
        stabilizers = lines
        n_qubits = 100
        
        current_stabs = stabilizers[:]
        print(f"Initial stabilizers: {len(current_stabs)}")
        
        # Check rank of initial stabilizers
        H_init = to_check_matrix(current_stabs, n_qubits)
        rank_init = get_rank_GF2(H_init)
        print(f"Initial rank: {rank_init}")
        if rank_init < len(current_stabs):
            print("WARNING: Initial stabilizers are not independent!")
            # Should we prune?
            # Let's prune to a basis.
            # But we need to keep the original ones if possible? No, we need a basis.
            # But we are asked to prepare a state stabilized by ALL of them.
            # If they are dependent but consistent, any basis works.
            # Let's find a basis.
            
            # Pruning strategy:
            independent_stabs = []
            current_rank = 0
            for s in current_stabs:
                mat = to_check_matrix(independent_stabs + [s], n_qubits)
                r = get_rank_GF2(mat)
                if r > current_rank:
                    independent_stabs.append(s)
                    current_rank = r
            print(f"Pruned to {len(independent_stabs)} independent stabilizers.")
            current_stabs = independent_stabs
        
        while len(current_stabs) < n_qubits:
            print(f"Current count: {len(current_stabs)}")
            
            H = to_check_matrix(current_stabs, n_qubits)
            current_rank = get_rank_GF2(H)
            
            M = np.zeros_like(H)
            M[:, :n_qubits] = H[:, n_qubits:] # hz
            M[:, n_qubits:] = H[:, :n_qubits] # hx
            
            null_basis = find_null_space(M)
            # print(f"Null space size: {len(null_basis)}")
            
            found_new = False
            for vec in null_basis:
                cand = vec_to_pauli(vec, n_qubits)
                
                # Check independence using Stim if possible
                # But Stim doesn't support "check if independent" easily for < N.
                # However, we can use our rank check, but it seems flaky.
                
                # Let's try to be extremely explicit about rank check.
                # Only trust rank increase if it is > current_rank.
                
                cand_mat = to_check_matrix([cand], n_qubits)
                combined = np.vstack([H, cand_mat])
                
                # Use a simpler rank check:
                # Use numpy linalg matrix_rank with GF(2) logic? No, numpy doesn't support GF(2).
                
                # Let's verify my get_rank_GF2 with a small example in main if needed.
                # But let's assume it's correct and I'm missing something about the data.
                
                # Maybe cand is indeed independent?
                # If Stim says it's redundant, then it IS redundant.
                # So my rank check says independent, but Stim says redundant.
                # This means my rank check returns higher rank for redundant row.
                
                # Example:
                # Row 0: 1 0
                # Row 1: 1 0
                # Pivot at (0,0).
                # Elim Row 1 -> 0 0.
                # Pivot row becomes 1.
                # Next col 1.
                # No pivot found.
                # Returns 1.
                # Correct.
                
                # Example 2:
                # Row 0: 1 0
                # Row 1: 0 1
                # Pivot at (0,0).
                # Elim Row 1 -> 0 1.
                # Pivot row 1.
                # Pivot at (1,1).
                # Returns 2.
                # Correct.
                
                # So what is happening?
                # Maybe `m` is being modified in a way that affects subsequent calls?
                # No, `m = mat.copy()`.
                
                # Maybe `H` is not what I think it is?
                # `H` is recomputed every loop.
                
                # Let's try to verify independence by checking if `cand` is a product of `current_stabs`.
                # We can do this by solving `x * H = cand` (vector-matrix eq).
                # If there is a solution x, then cand is dependent.
                # Since H has full row rank (we assume), we can check this.
                # H^T x^T = cand^T.
                
                # Let's implement `is_dependent(H, cand_vec)`.
                
                is_dep = False
                
                # Check if cand_vec is in row span of H
                # We can check if rank(H) == rank(H + cand).
                pass
                
                new_rank = get_rank_GF2(combined)
                if new_rank > current_rank:
                     # Double check with Stim?
                     # No way to check easily.
                     pass
                     
                if new_rank > current_rank:
                     # If Stim says it's redundant, then my rank check is wrong.
                     # But why?
                     # Maybe the 'cand' string format is different?
                     # I am using `stim.PauliString(s)` which normalizes.
                     # But `cand` string comes from `vec_to_pauli`.
                     # Let's normalize `cand`.
                     
                     cand_ps = stim.PauliString(cand)
                     if cand_ps in [stim.PauliString(s) for s in current_stabs]:
                         # Only checks for exact match
                         continue
                         
                     print(f"Found independent: {cand}")
                     current_stabs.append(str(cand_ps))
                     found_new = True
                     break
            
            if not found_new:
                print("Could not find independent stabilizer!")
                break
        
        if len(current_stabs) == n_qubits:
            print("Set complete.")
            t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in current_stabs])
            c = t.to_circuit()
            
            # Verify correctness
            sim = stim.TableauSimulator()
            sim.do(c)
            
            valid = True
            for i, s in enumerate(stabilizers):
                val = sim.measure_expectation(stim.PauliString(s))
                if val != 1:
                    print(f"Stabilizer {i} failed! Expectation: {val}")
                    valid = False
                    break
            
            if valid:
                print("Verification successful!")
                with open("circuit_100.stim", "w") as f:
                    f.write(str(c))
            else:
                print("Verification failed.")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
