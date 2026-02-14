import stim
import numpy as np
import sys

def char_to_int(c):
    if c == 'I': return 0
    if c == 'X': return 1
    if c == 'Z': return 3
    if c == 'Y': return 2
    return 0

def to_check_matrix(stabs, n):
    mat = np.zeros((len(stabs), 2*n), dtype=int)
    for i, s in enumerate(stabs):
        for k in range(n):
            if k < len(s):
                p = char_to_int(s[k])
                if p == 1 or p == 2: # X or Y
                    mat[i, k] = 1
                if p == 3 or p == 2: # Z or Y
                    mat[i, k + n] = 1
    return mat

def get_rank_GF2(mat):
    # Make sure to copy and use integer types, although python handles large ints automatically
    # But for numpy arrays of dtype=int, XOR works as expected only if values are 0/1.
    m = mat.copy()
    rows, cols = m.shape
    p_row = 0
    for j in range(cols):
        if p_row >= rows: break
        pivot = -1
        for i in range(p_row, rows):
            if m[i, j] == 1:
                pivot = i
                break
        if pivot == -1: continue
        
        # Swap rows
        if pivot != p_row:
            temp = m[p_row].copy()
            m[p_row] = m[pivot]
            m[pivot] = temp
        
        # Eliminate
        for i in range(rows):
            if i != p_row and m[i, j] == 1:
                m[i] ^= m[p_row]
        p_row += 1
    
    # Check if any zero rows were counted as rank? No, p_row is incremented only when pivot found.
    return p_row

def main():

def find_null_space(mat):
    # Find basis for null space of mat * x = 0 over GF(2)
    m = mat.copy()
    rows, cols = m.shape
    
    # Gaussian elimination to RREF
    p_row = 0
    pivots = []
    # Using float to avoid overflow? No, GF(2) uses XOR.
    # But numpy uses standard arithmetic. We need explicit XOR.
    
    # Transpose to find kernel of A^T? No.
    # Ax = 0.
    
    # Let's do Gaussian elimination on M.
    # Identify free variables.
    
    for j in range(cols):
        if p_row >= rows: break
        pivot = -1
        for i in range(p_row, rows):
            if m[i, j]:
                pivot = i
                break
        if pivot == -1: continue
        
        m[[p_row, pivot]] = m[[pivot, p_row]]
        
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
        
        while len(current_stabs) < n_qubits:
            print(f"Current count: {len(current_stabs)}")
            
            # 1. Build check matrix H
            H = to_check_matrix(current_stabs, n_qubits)
            current_rank = get_rank_GF2(H)
            print(f"Current rank: {current_rank}")
            
            # 2. Build M for symplectic constraint
            # Rows of M are symplectic duals of rows of H
            # For each row h of H, we want v such that <h, v>_symp = 0
            # h = [hx, hz]. v = [vx, vz].
            # hx . vz + hz . vx = 0
            # [hz, hx] . [vx, vz] = 0
            
            M = np.zeros_like(H)
            M[:, :n_qubits] = H[:, n_qubits:] # hz -> first half
            M[:, n_qubits:] = H[:, :n_qubits] # hx -> second half
            
            # 3. Find null space of M
            null_basis = find_null_space(M)
            print(f"Null space size: {len(null_basis)}")
            
            # 4. Find independent vector
            found_new = False
            for vec in null_basis:
                cand = vec_to_pauli(vec, n_qubits)
                
                # Check independence
                # Quick check: does it increase rank?
                cand_mat = to_check_matrix([cand], n_qubits)
                combined = np.vstack([H, cand_mat])
                new_rank = get_rank_GF2(combined)
                
                if new_rank > current_rank:
                    print(f"Found independent: {cand}")
                    current_stabs.append(cand)
                    found_new = True
                    break
            
            if not found_new:
                print("Could not find independent stabilizer!")
                break
        
        if len(current_stabs) == n_qubits:
            print("Set complete.")
            t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in current_stabs])
            c = t.to_circuit()
            
            # Verify correctness against ORIGINAL stabilizers
            # Stim's tableau simulator initialized to |0> then run circuit
            sim = stim.TableauSimulator()
            sim.do(c)
            
            # Check all original stabilizers
            valid = True
            for i, s in enumerate(stabilizers):
                # measure_expectation returns +1 or -1
                # expectation of Pauli P on state |psi>
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
