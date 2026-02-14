import stim
import numpy as np

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

def to_binary(p, n=42):
    row = np.zeros(2*n, dtype=np.uint8)
    for k in range(n):
        val = p[k]
        if val == 1 or val == 2: row[k] = 1 
        if val == 3 or val == 2: row[k + n] = 1 
    return row

def from_binary(row, n=42):
    s = ""
    for k in range(n):
        x = row[k]
        z = row[k+n]
        if x and z: s += "Y"
        elif x: s += "X"
        elif z: s += "Z"
        else: s += "I"
    return stim.PauliString(s)

def matrix_rank(matrix):
    if len(matrix) == 0: return 0
    m = matrix.copy()
    rs, cs = m.shape
    pr = 0
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

def solve_and_verify():
    num_qubits = 42
    stabs = [stim.PauliString(s) for s in stabilizers]
    
    current_rows = np.array([to_binary(s) for s in stabs], dtype=np.uint8)
    rank = matrix_rank(current_rows)
    print(f"Rank: {rank}")
    
    # Complete the set
    J = np.zeros((2*num_qubits, 2*num_qubits), dtype=np.uint8)
    for k in range(num_qubits):
        J[k, k+num_qubits] = 1
        J[k+num_qubits, k] = 1
        
    A = (current_rows @ J) % 2
    
    # Null space
    rows_A, cols_A = A.shape
    mat = A.copy()
    pivots = []
    pivot_row = 0
    pivot_col_to_row = {}
    
    for c in range(cols_A):
        if pivot_row >= rows_A: break
        swap = -1
        for r in range(pivot_row, rows_A):
            if mat[r, c] == 1:
                swap = r
                break
        if swap != -1:
            mat[[pivot_row, swap]] = mat[[swap, pivot_row]]
            for r in range(rows_A):
                if r != pivot_row and mat[r, c] == 1:
                    mat[r] ^= mat[pivot_row]
            pivot_col_to_row[c] = pivot_row
            pivots.append(c)
            pivot_row += 1
            
    free_vars = [c for c in range(cols_A) if c not in pivots]
    
    null_basis = []
    for free in free_vars:
        vec = np.zeros(cols_A, dtype=np.uint8)
        vec[free] = 1
        for p in reversed(pivots):
            r = pivot_col_to_row[p]
            val = 0
            for k in range(p+1, cols_A):
                if mat[r, k]: val ^= vec[k]
            vec[p] = val
        null_basis.append(vec)
        
    candidates = [from_binary(v) for v in null_basis]
    
    final_stabs = list(stabs)
    current_mat = current_rows.copy()
    current_rank = rank
    
    for cand in candidates:
        if len(final_stabs) == 42: break
        
        commutes = True
        for i in range(38, len(final_stabs)):
            if not cand.commutes(final_stabs[i]):
                commutes = False
                break
        if not commutes: continue
        
        cand_vec = to_binary(cand)
        test_mat = np.vstack([current_mat, cand_vec])
        new_rank = matrix_rank(test_mat)
        
        if new_rank > current_rank:
            final_stabs.append(cand)
            current_mat = test_mat
            current_rank = new_rank
            
    if len(final_stabs) != 42:
        print(f"Failed to complete set. {len(final_stabs)}")
        return

    # Generate circuit
    t = stim.Tableau.from_stabilizers(final_stabs)
    c = t.to_circuit("elimination")
    
    # Verify
    print("Verifying circuit...")
    sim = stim.TableauSimulator()
    sim.do(c)
    
    failures = 0
    for i, s in enumerate(stabs):
        # We want expectation +1.
        # stim.TableauSimulator.peek_observable_expectation(observable)
        # Returns +1, -1, or 0 (random).
        exp = sim.peek_observable_expectation(s)
        if exp != 1:
            print(f"Stabilizer {i} failed. Expectation: {exp}")
            failures += 1
            
    if failures == 0:
        print("Verification SUCCESS: All stabilizers preserved.")
        with open("clean_circuit.stim", "w") as f:
            f.write(str(c))
        print("Wrote circuit to clean_circuit.stim")
    else:
        print(f"Verification FAILED: {failures} stabilizers not preserved.")

if __name__ == "__main__":
    solve_and_verify()
