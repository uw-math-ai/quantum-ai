import stim
import numpy as np

def solve():
    x_stabilizers = [
        "XXIIIIXXIIIIXXIIIIXXIIIIXXIIIIXXIIII",
        "XIXIIIXIXIIIXIXIIIXIXIIIXIXIIIXIXIII",
        "XIIXIIXIIXIIXIIXIIXIIXIIXIIXIIXIIXII",
        "XIIIXIXIIIXIXIIIXIXIIIXIXIIIXIXIIIXI",
        "XXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIXXXXXXIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIXXXXXXIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIXXXXXXIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIXXXXXXIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXX"
    ]
    
    z_stabilizers = [
        "ZZIIIIZZIIIIZZIIIIZZIIIIZZIIIIZZIIII",
        "ZIZIIIZIZIIIZIZIIIZIZIIIZIZIIIZIZIII",
        "ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII",
        "ZIIIZIZIIIZIZIIIZIZIIIZIZIIIZIZIIIZI",
        "ZZZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIZZZZZZIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIZZZZZZIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIZZZZZZIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIZZZZZZIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZZZ"
    ]
    
    num_qubits = 36
    
    # 1. Complete the stabilizer set
    
    def null_space_gf2(mat):
        m = mat.copy()
        rows, cols = m.shape
        aug = np.hstack([m.T, np.eye(cols, dtype=int)])
        pivot_row = 0
        r, c = aug.shape
        for col in range(rows):
            if pivot_row >= r: break
            pivot = -1
            for row in range(pivot_row, r):
                if aug[row, col] == 1:
                    pivot = row
                    break
            if pivot != -1:
                aug[[pivot_row, pivot]] = aug[[pivot, pivot_row]]
                for row in range(r):
                    if row != pivot_row and aug[row, col] == 1:
                        aug[row] ^= aug[pivot_row]
                pivot_row += 1
        basis = []
        for i in range(r):
            if not np.any(aug[i, :rows]):
                basis.append(aug[i, rows:])
        return np.array(basis)

    h_x = np.zeros((len(x_stabilizers), num_qubits), dtype=int)
    for i, s in enumerate(x_stabilizers):
        for j, c in enumerate(s):
            if c == 'X': h_x[i, j] = 1
                
    z_candidates = null_space_gf2(h_x)
    
    h_z = np.zeros((len(z_stabilizers), num_qubits), dtype=int)
    for i, s in enumerate(z_stabilizers):
        for j, c in enumerate(s):
            if c == 'Z': h_z[i, j] = 1
    
    final_z_vectors = list(h_z)
    
    def rank_gf2(mat):
        m = np.array(mat)
        if m.size == 0: return 0
        rows, cols = m.shape
        pivot_row = 0
        for col in range(cols):
            if pivot_row >= rows: break
            pivot = -1
            for r in range(pivot_row, rows):
                if m[r, col] == 1:
                    pivot = r
                    break
            if pivot != -1:
                m[[pivot_row, pivot]] = m[[pivot, pivot_row]]
                for r in range(rows):
                    if r != pivot_row and m[r, col] == 1:
                        m[r] ^= m[pivot_row]
                pivot_row += 1
        return pivot_row

    for cand in z_candidates:
        if rank_gf2(final_z_vectors + [cand]) > len(final_z_vectors):
            final_z_vectors.append(cand)
            
    print(f"Total Z stabilizers: {len(final_z_vectors)}")
    
    # Matrices
    mat_x = h_x.copy() # 10x36
    mat_z = np.array(final_z_vectors) # 26x36
    
    ops = [] # (gate, args)
    
    # Since we modify mat_x and mat_z, we define helpers.
    def op_swap(q1, q2):
        if q1 == q2: return
        mat_x[:, [q1, q2]] = mat_x[:, [q2, q1]]
        mat_z[:, [q1, q2]] = mat_z[:, [q2, q1]]
        ops.append(("SWAP", [q1, q2]))
        
    def op_cnot(c, t):
        if c == t: return
        # X: col c adds to col t
        mat_x[:, t] ^= mat_x[:, c]
        # Z: col t adds to col c
        mat_z[:, c] ^= mat_z[:, t]
        ops.append(("CX", [c, t]))
        
    # Phase 1: Diagonalize X-matrix (rows 0-9) to [I | 0] using cols 0-9.
    for r in range(10):
        pivot_col = -1
        # Look in cols >= r (standard)
        for j in range(r, num_qubits):
            if mat_x[r, j] == 1:
                pivot_col = j
                break
        if pivot_col == -1:
            print(f"Error: X matrix rank < 10 at row {r}")
            return
            
        op_swap(r, pivot_col)
        
        # Eliminate other entries in row r
        for j in range(num_qubits):
            if j != r and mat_x[r, j] == 1:
                op_cnot(r, j)
                
    # Phase 2: Diagonalize Z-matrix (rows 0-25) to [0 | I] using cols 10-35.
    # Note: cols 0-9 of Z-matrix are 0 (ensured by commutation with X_0...X_9).
    
    # But wait, CNOTs in Phase 1 affect Z-matrix.
    # Specifically, CNOT(c, t) adds Z_t to Z_c.
    # If t > 9 and c < 10, Z_t adds to Z_c (in first 10 cols).
    # This might make first 10 cols non-zero?
    # Yes.
    # But does it matter?
    # The X-stabilizers are X_0...X_9.
    # The Z-stabilizers S_Z are now mixed.
    # But S_Z still commutes with X_i.
    # X_i has X only on i.
    # If S_Z has Z on i, it anticommutes.
    # So S_Z must NOT have Z on i.
    # So even after mixing, the Z-stabilizers must be 0 on cols 0-9.
    # Let's verify this reasoning.
    # CNOT(c, t): X_c -> X_c X_t.
    # Z_t -> Z_c Z_t.
    # Commutation preserved.
    # If we start with valid stabilizers, we end with valid stabilizers.
    # So the Z-stabilizers will always be 0 on cols 0-9 if X-stabilizers are X_0...X_9.
    # So we don't need to worry about cols 0-9 in Phase 2.
    
    # Phase 2: Diagonalize Z-matrix (rows 0-25) to [0 | I] using cols 10-35.
    
    # We need to process rows. But to ensure we can always find a pivot for row r at col 10+r,
    # we need to make sure that the rows are linearly independent.
    # We know they are.
    # The issue is that we need to use previous pivots to clear the current row's entries in previous columns.
    
    # Let's track which column is pivot for which row?
    # No, we force row r to have pivot at 10+r.
    
    for r in range(26):
        target_col = 10 + r
        
        # 1. Eliminate entries in columns < target_col (which are pivots for previous rows).
        # We must do this before finding pivot for current row?
        # Actually, if we did full Gaussian elimination (clearing ABOVE and BELOW),
        # then column c (where c < target_col) should only have a 1 in row (c-10).
        # So if row r has a 1 in column c, we add row (c-10) to row r.
        # But we implement row operations by column operations on the stabilizer matrix?
        # WAIT.
        # If we do CNOT(c, t), we add row c to row t in the CHECK MATRIX?
        # No.
        # Stabilizers S_i transform to S_i'.
        # We are modifying the stabilizers.
        # CNOT(c, t) transforms:
        # X_c -> X_c X_t
        # Z_t -> Z_c Z_t
        # This mixes columns in the check matrix.
        # This is column operations on the check matrix.
        
        # We want to clear the check matrix to I.
        # So we use column operations.
        # To clear entry mat[r, j], we need to add another column k to column j?
        # No, we add column j to column k?
        # If we want to zero out mat[r, j] using mat[r, k] (where mat[r, k]=1):
        # We add col k to col j (if we are in X matrix).
        # Or add col j to col k (if we are in Z matrix)?
        # Let's check Z-logic again.
        # CNOT(c, t): Z_t -> Z_c Z_t.
        # Z_c (control) gets Z_t (target) added to it.
        # So we can add any column t to column c.
        # So to clear column c (make it 0) using column t (where mat[r, t]=1):
        # We do CNOT(c, t).
        # This adds Z_t to Z_c. So mat_z[:, c] ^= mat_z[:, t].
        # Yes.
        
        # So, for row r, we want to make it a unit vector (0...0 1 0...0) with 1 at target_col.
        # 1. Find a column j >= target_col that has 1.
        pivot_col = -1
        for j in range(target_col, num_qubits):
            if mat_z[r, j] == 1:
                pivot_col = j
                break
        
        # If no pivot in >= target_col, maybe it's in < target_col?
        # If so, we should have cleared it using previous rows.
        # But wait, did we clear previous columns for THIS row?
        # In standard Gaussian elimination, when we process row k (pivot at k), we clear col k in ALL rows (including future rows).
        # My previous code:
        # for j in range(10, num_qubits): if j != target_col ... op_cnot(target_col, j)
        # This clears col j using col target_col.
        # It clears col j in ALL rows?
        # No, CNOT affects ALL rows.
        # So yes, it clears col j in all rows.
        # BUT, it uses row r's pivot to clear other columns.
        # It does NOT clear row r's other columns using OTHER rows' pivots.
        
        # The problem is that row r might have 1s in columns < target_col.
        # These columns are pivots for PREVIOUS rows.
        # We must use previous rows' pivots to clear these entries in row r.
        # But we are doing column operations.
        # We cannot "use a row to clear a row".
        # We use a column to clear a column.
        
        # Wait, if we clear col j using pivot col k:
        # We make col j zero in row r.
        # But we affect other rows.
        # If row r' has 1 in col k, it now gets added to row r' in col j.
        # This is standard column reduction.
        
        # The issue "Z matrix rank < 26 at row 10" means:
        # Row 10 has 0s in cols >= 20.
        # But it has 1s in cols < 20.
        # Specifically 13-19.
        # Columns 13-19 are pivots for rows 3-9 (of Z matrix).
        # We should have cleared columns 13-19 in ALL rows when we processed rows 3-9.
        # Did we?
        # In step k (pivot at col 10+k), we cleared all other cols j != 10+k.
        # Including cols > 10+k AND cols < 10+k?
        # My code: `for j in range(10, num_qubits): if j != target_col ...`
        # Yes, it iterates over ALL j in 10..35.
        # So it should have cleared col j in ALL rows.
        # So why is row 10 having 1s in cols 13-19?
        
        # Maybe I am swapping rows? No, swapping columns.
        # Maybe the order is wrong?
        # `op_cnot(target_col, j)`:
        # Z: col t adds to col c.
        # We want to add pivot column (target_col) to other column (j) to zero it out?
        # Pivot col has 1 in row r. Other col has 1 in row r.
        # Adding pivot to other makes other 0.
        # op_cnot(c, t): Z_c ^= Z_t.
        # So if we want Z_j ^= Z_pivot, we need CNOT(j, pivot).
        # My code: `op_cnot(target_col, j)`.
        # This does Z_{target_col} ^= Z_j.
        # This adds OTHER column to PIVOT column!
        # This CLEARS THE PIVOT COLUMN?
        # No, this is wrong.
        
        # Correct direction for Z:
        # CNOT(c, t) -> Z_c += Z_t.
        # We want Z_j += Z_pivot.
        # So we need CNOT(j, pivot).
        # c = j, t = pivot.
        
        # Let's check X direction too.
        # CNOT(c, t) -> X_t += X_c.
        # We want X_j += X_pivot.
        # So we need CNOT(pivot, j).
        # c = pivot, t = j.
        
        # So for X-matrix (Phase 1):
        # We used `op_cnot(r, j)`.
        # r is pivot. j is other.
        # c=r, t=j.
        # X_j += X_r.
        # This is CORRECT.
        
        # For Z-matrix (Phase 2):
        # We used `op_cnot(target_col, j)`.
        # target_col is pivot. j is other.
        # c=target_col, t=j.
        # Z_{target_col} += Z_j.
        # This adds other to pivot.
        # This is WRONG.
        # We want Z_j += Z_{target_col}.
        # So we need `op_cnot(j, target_col)`.
        
    for r in range(26):
        target_col = 10 + r
        # Look for pivot in cols >= target_col
        pivot_col = -1
        for j in range(target_col, num_qubits):
            if mat_z[r, j] == 1:
                pivot_col = j
                break
        
        if pivot_col == -1:
            print(f"Error: Z matrix rank < 26 at row {r}")
            return
            
        op_swap(target_col, pivot_col)
        
        # Eliminate other entries in row r (cols 10-35)
        # Use CNOT(j, target_col) to add Z_target to Z_j
        for j in range(10, num_qubits):
            if j != target_col and mat_z[r, j] == 1:
                op_cnot(j, target_col)

                
    # Generate circuit
    # Inverse of ops
    c = stim.Circuit()
    
    # 1. Prepare |+> on 0-9, |0> on 10-35
    for i in range(10):
        c.append("H", [i])
        
    # 2. Apply inverse ops
    for gate, args in reversed(ops):
        c.append(gate, args)
        
    # Output to file
    with open("circuit.stim", "w") as f:
        f.write(str(c))
        
    print("Circuit generated in circuit.stim")

if __name__ == "__main__":
    solve()
