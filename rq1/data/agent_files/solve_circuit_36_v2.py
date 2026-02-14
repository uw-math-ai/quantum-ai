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
    
    # Helper for GF(2) rank
    def rank_gf2(mat):
        m = mat.copy()
        rows, cols = m.shape
        pivot_row = 0
        for col in range(cols):
            if pivot_row >= rows:
                break
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
        
    # Helper for finding null space
    def null_space_gf2(mat):
        # Solves M * x = 0
        # Transpose M, augment with I, RREF.
        # Zero rows in RREF(M^T) correspond to basis vectors in I.
        m = mat.copy()
        rows, cols = m.shape
        # Augment: [M^T | I]
        aug = np.hstack([m.T, np.eye(cols, dtype=int)])
        
        # RREF
        pivot_row = 0
        r, c = aug.shape
        for col in range(rows): # only reduce the M^T part
            if pivot_row >= r:
                break
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
        
        # Identify zero rows in the left part
        basis = []
        for i in range(r):
            if not np.any(aug[i, :rows]):
                basis.append(aug[i, rows:])
                
        return np.array(basis)

    # Matrix for X stabilizers
    h_x = np.zeros((len(x_stabilizers), num_qubits), dtype=int)
    for i, s in enumerate(x_stabilizers):
        for j, c in enumerate(s):
            if c == 'X':
                h_x[i, j] = 1
                
    # Find Z candidates (commute with X => orthogonal to rows of H_X)
    z_candidates = null_space_gf2(h_x)
    print(f"Found {len(z_candidates)} Z candidates")
    
    # Current Z stabilizers
    h_z = np.zeros((len(z_stabilizers), num_qubits), dtype=int)
    for i, s in enumerate(z_stabilizers):
        for j, c in enumerate(s):
            if c == 'Z':
                h_z[i, j] = 1
    
    current_z_vectors = list(h_z)
    
    # Add independent candidates
    final_z_vectors = list(current_z_vectors)
    for cand in z_candidates:
        test_set = np.array(final_z_vectors + [cand])
        if rank_gf2(test_set) > len(final_z_vectors):
            final_z_vectors.append(cand)
            
    print(f"Total Z stabilizers: {len(final_z_vectors)}")
    
    if len(final_z_vectors) + len(x_stabilizers) != 36:
        print("Error: Could not complete stabilizer set.")
        # But wait, we might have fewer than 36 independent stabilizers if the problem is underspecified?
        # But for state prep we need a full set.
        # Actually, 10 X + 26 Z = 36. That is correct.
    
    # 2. Generate Circuit
    
    # We have a CSS code:
    # X stabilizers: S_X (10)
    # Z stabilizers: S_Z (26)
    
    # We can prepare the state by:
    # 1. Prepare + states for qubits involved in X stabilizers?
    # No, standard CSS prep:
    # Initialize all in |0>
    # Apply H to X-logical qubits?
    # Use Stim's Tableau directly.
    
    sim = stim.TableauSimulator()
    # But Simulator doesn't give us the circuit.
    
    # Let's construct a Tableau object representing the target state.
    # We need to specify the stabilizers and destabilizers.
    # Finding destabilizers is hard.
    
    # Alternative:
    # Gaussian elimination on the Tableau.
    # Start with identity Tableau (stabilizers Z_0...Z_35).
    # Apply gates to transform rows.
    # Since we only have X and Z stabilizers (CSS), we can do it with CNOTs and Hadamards.
    
    # Actually, simply:
    # Since we have 10 X stabilizers and 26 Z stabilizers.
    # Can we find a basis change (CNOTs) such that X stabilizers become X_0...X_9
    # and Z stabilizers become Z_10...Z_35?
    # Then we just apply H on 0...9?
    # Let's try to diagonalize the stabilizer matrix.
    
    # Stabilizer matrix M (36 x 72)
    # Rows 0-9: X stabilizers (X part only, Z part 0)
    # Rows 10-35: Z stabilizers (Z part only, X part 0)
    
    # X-part of M (36 x 36):
    # Rows 0-9: H_X (10 x 36)
    # Rows 10-35: 0
    
    # Z-part of M (36 x 36):
    # Rows 0-9: 0
    # Rows 10-35: H_Z_full (26 x 36)
    
    # We want to transform this to:
    # X-part:
    # X_0 ... X_9 -> Identity on first 10 cols?
    # Z-part:
    # Z_10 ... Z_35 -> Identity on last 26 cols?
    
    # Gaussian elimination with CNOTs (column operations on X and Z parts simultaneously).
    # CNOT(i, j): adds col i to col j in X-part, adds col j to col i in Z-part.
    # Swap(i, j): swaps cols.
    
    # Let's implement this Gaussian elimination to clear the matrix.
    # Operations recorded as circuit.
    # But we are doing column operations on the stabilizer matrix (which corresponds to row operations on the state vector basis?).
    # Wait, applying unitary U transforms stabilizers S to U S U^dagger.
    # This corresponds to row operations on the check matrix? No.
    # The check matrix rows are the stabilizers.
    # The columns are the qubits.
    # Unitary operations mix columns.
    # We want to simplify the rows (generators) to single Pauli operators (e.g. Z_i).
    # Then the inverse circuit prepares the state from Z_i basis.
    
    # So:
    # 1. Construct matrix of stabilizers.
    # 2. Apply Clifford gates (CNOT, H, S) to diagonalize it to Z_0, ..., Z_35.
    #    Wait, we want to map S_i -> Z_i.
    #    Then the circuit is U.
    #    State |psi> is stabilized by S_i.
    #    U |psi> is stabilized by U S_i U^dagger = Z_i.
    #    So U |psi> = |0...0>.
    #    So |psi> = U^dagger |0...0>.
    
    # So we need to find U that maps S_i -> Z_i.
    # Operations allowed:
    # - CNOT(i, j):
    #   X_i -> X_i X_j
    #   Z_j -> Z_i Z_j
    # - H(i):
    #   X_i <-> Z_i
    # - S(i):
    #   X_i -> Y_i
    #   Z_i -> Z_i
    
    # Algorithm:
    # 1. Gaussian elimination to make X-part diagonal.
    #    For each row i (stabilizer S_i), try to make it X_i.
    #    But we have 36 stabilizers.
    #    First 10 are X-type. Next 26 are Z-type.
    #    We can map X-type ones to X_0...X_9?
    #    And Z-type ones to Z_10...Z_35?
    #    If we do that, we get stabilizers {X_0...X_9, Z_10...Z_35}.
    #    The state stabilized by this is |+>^{10} |0>^{26}.
    #    This is easy to prepare: H on 0-9, nothing on 10-35.
    #    So we find U such that U S_i U^dagger = Canonical_i.
    #    Then |psi> = U^dagger |Canonical>.
    
    # Let's implement this.
    
    circuit = stim.Circuit()
    
    # Working matrix of stabilizers.
    # List of [X_vector, Z_vector]
    # X_vector, Z_vector are length 36 bitmasks.
    
    stabs = []
    # Add X stabilizers
    for i in range(len(x_stabilizers)):
        x_vec = np.zeros(num_qubits, dtype=int)
        for j, c in enumerate(x_stabilizers[i]):
            if c == 'X': x_vec[j] = 1
        stabs.append((x_vec, np.zeros(num_qubits, dtype=int)))
        
    # Add Z stabilizers
    for z_vec in final_z_vectors:
        stabs.append((np.zeros(num_qubits, dtype=int), z_vec))
        
    # We have 36 stabilizers.
    # We want to reduce them to single qubit operators.
    # We will record the gates in `circuit`.
    # Since we want U^dagger, and we find U, we should append gates to the beginning of the inverse circuit?
    # Or just record U and then invert it.
    # Stim circuits are easy to invert if they only contain Unitaries.
    
    gates = [] # List of (name, targets)
    
    def apply_cnot(c, t):
        # Update stabilizers
        # X_c -> X_c X_t
        # Z_t -> Z_c Z_t
        for i in range(36):
            x, z = stabs[i]
            # Update X: if X_c is present, flip X_t
            if x[c]: x[t] ^= 1
            # Update Z: if Z_t is present, flip Z_c
            if z[t]: z[c] ^= 1
        gates.append(("CX", [c, t]))

    def apply_h(q):
        # X_q <-> Z_q
        for i in range(36):
            x, z = stabs[i]
            x[q], z[q] = z[q], x[q]
        gates.append(("H", [q]))
        
    def apply_s(q):
        # X_q -> Y_q = X_q Z_q
        # Z_q -> Z_q
        for i in range(36):
            x, z = stabs[i]
            # If x[q] is 1, we add z[q] to z[q] (flip it)?
            # Y = XZ. In symplectic notation: (1, 0) -> (1, 1).
            if x[q]: z[q] ^= 1
        gates.append(("S", [q]))

    # Simplification loop
    # We want to clear the table to identity matrix?
    # We want stabilizer i to be Z_i (or X_i).
    
    # Strategy:
    # 1. Eliminate X components to make them diagonal-ish?
    # Actually, standard algorithm for "diagonalizing a stabilizer state":
    # Make the X-matrix full rank on first k columns?
    
    # We want to map S_i to Z_i.
    # Process column by column (qubit by qubit).
    # For qubit q:
    # Find a stabilizer S_k (k >= q) that has X_q or Z_q.
    # Use it to eliminate others.
    # Finally move it to S_q and transform it to Z_q.
    
    for q in range(num_qubits):
        # 1. Find a stabilizer k >= q with X_q = 1.
        pivot_k = -1
        for k in range(q, num_qubits):
            if stabs[k][0][q]:
                pivot_k = k
                break
        
        if pivot_k != -1:
            # Found X_q.
            # Swap stabilizers k and q (just relabeling, no gate).
            stabs[q], stabs[pivot_k] = stabs[pivot_k], stabs[q]
            
            # Now S_q has X_q = 1.
            # Eliminate X_q from other stabilizers k > q.
            # Wait, we can only add stabilizers to each other?
            # No, we are finding a unitary U that transforms stabilizers.
            # We are NOT doing row operations on the stabilizer matrix.
            # We are doing COLUMN operations (gates) to transform the stabilizers.
            # If we apply CNOT(q, j), we affect column q and j.
            # We want to use gates to make S_q = Z_q (or X_q).
            pass
            
            # This logic is tricky.
            # Correct logic:
            # We want to reduce the stabilizer matrix to Identity (Z basis).
            # Stabilizer matrix has rows = stabilizers.
            # We apply gates (column ops) to simplify rows.
            
            # Step 1: Make X-matrix of first n rows (if possible) triangular?
            # No.
            
            # Let's use a simpler heuristic for CSS states.
            # We have X-stabilizers (only X) and Z-stabilizers (only Z).
            # Can we just diagonalize the X-matrix using CNOTs?
            # X-matrix H_X (10 x 36).
            # Do Gaussian elimination with column ops (CNOTs, Swaps) to get [I | 0].
            # CNOT(c, t) adds col c to col t.
            # After this, the first 10 stabilizers are X_0, ..., X_9.
            # And we have transformed the Z-stabilizers too.
            # But CNOTs preserve the CSS structure?
            # CNOT propagates X from control to target.
            # Z from target to control.
            # So X-only stabilizers stay X-only?
            # Yes, if we only start with X stabilizers.
            # But we have Z stabilizers too. They will change but stay Z-only?
            # Yes!
            # If S is X-only, it has Z=0. CNOT: X_c -> X_c X_t. Z part stays 0.
            # If S is Z-only, it has X=0. CNOT: Z_t -> Z_c Z_t. X part stays 0.
            # So we can diagonalize H_X and H_Z independently?
            # Not quite, CNOTs affect both.
            
            # Algorithm:
            # 1. Diagonalize H_X (first 10 stabilizers).
            #    Use CNOTs and SWAPs to transform H_X to [I_10 | 0].
            #    This maps X-stabilizers to X_0...X_9.
            # 2. Now consider H_Z (remaining 26 stabilizers).
            #    The operations in step 1 changed H_Z.
            #    But they are still Z-only.
            #    The first 10 columns of H_Z might be non-zero.
            #    But X_0...X_9 commute with Z-stabilizers.
            #    X_i commutes with Z-stab means Z-stab doesn't have Z_i?
            #    X_i and Z_j commute unless i=j.
            #    So if X_i is a stabilizer, and S is another stabilizer (commuting), then S cannot have Z_i.
            #    Wait, if X_i is stabilizer, and S has Z_i, they anticommute.
            #    So S must NOT have Z_i.
            #    So the first 10 columns of H_Z MUST be 0.
            #    So H_Z is effectively 0 on first 10 cols.
            #    So we only need to diagonalize the last 26 cols of H_Z.
            #    Use CNOTs/SWAPs on qubits 10-35 to transform H_Z to [0 | I_26].
            #    This maps Z-stabilizers to Z_10...Z_35.
            
            # So the state is now stabilized by X_0...X_9 and Z_10...Z_35.
            # This is |+>^{10} |0>^{26}.
            # The circuit we found (call it V) does:
            # S_original -> {X_0...X_9, Z_10...Z_35}.
            # So V |psi> = |+...0...>.
            # So |psi> = V^dagger |+...0...>.
            
            # Preparation circuit:
            # 1. Prepare |+> on 0-9, |0> on 10-35.
            #    (H on 0-9).
            # 2. Apply V^dagger.
            
    # Implementation of this algorithm:
    
    # Track X-matrix (10 x 36)
    # Track Z-matrix (26 x 36)
    # We apply ops to these matrices and record them.
    
    mat_x = h_x.copy()
    mat_z = np.array(final_z_vectors)
    
    ops = [] # List of (gate, args)
    
    def op_swap(q1, q2):
        if q1 == q2: return
        mat_x[:, [q1, q2]] = mat_x[:, [q2, q1]]
        mat_z[:, [q1, q2]] = mat_z[:, [q2, q1]]
        ops.append(("SWAP", [q1, q2]))
        
    def op_cnot(c, t):
        if c == t: return
        # X: col c adds to col t
        mat_x[:, t] ^= mat_x[:, c]
        # Z: col t adds to col c (backwards!)
        mat_z[:, c] ^= mat_z[:, t]
        ops.append(("CX", [c, t]))
        
    # 1. Gaussian elimination on mat_x (rows 0-9) to get I on cols 0-9.
    current_col = 0
    for r in range(10):
        # Find pivot in row r, col >= current_col
        # Actually we want to clear columns.
        # But we want to make the matrix [I | 0].
        # So we process rows 0..9. For each row, pick a column to be 1.
        
        # Find a column j >= r such that mat_x[r, j] == 1.
        pivot_col = -1
        for j in range(r, num_qubits):
            if mat_x[r, j] == 1:
                pivot_col = j
                break
        
        if pivot_col == -1:
            print(f"Error: X matrix rank < 10 at row {r}")
            return
            
        # Bring pivot to col r
        op_swap(r, pivot_col)
        
        # Now mat_x[r, r] is 1.
        # Eliminate other entries in this row?
        # No, we want to make OTHER columns 0.
        # So for j != r, if mat_x[r, j] == 1, add col r to col j (CNOT r->j).
        for j in range(num_qubits):
            if j != r and mat_x[r, j] == 1:
                op_cnot(r, j)
                
        # Now row r is 1 at r and 0 elsewhere.
        # But wait, CNOT(r, j) affects other rows too.
        # Does it ruin previous rows?
        # Previous rows k < r have 1 at k and 0 elsewhere.
        # If we do CNOT(r, j) where r > k, does it affect col k?
        # No, source is r, target is j.
        # Does it affect col j? Yes.
        # But row k has 0 at r (since r > k, and we cleared col r for previous rows? No).
        # We need to ensure that previous pivot columns remain clean.
        # The standard Gaussian elimination clears *columns* below the pivot.
        # Here we are doing column operations to clear *entries* in the row.
        # Once row r is (0...0 1 0...0) (at pos r), it stays that way if we don't use col r as target.
        # In later steps (row r+1), we use cols > r.
        # If we target col j > r using col k > r, we don't touch col r.
        # So it is safe.
        
        # Wait, what if we use col r as source?
        # In step r, we use col r as source to clear col j.
        # That's fine.
    
    # After 10 steps, mat_x should be [I_10 | 0].
    # And mat_z first 10 cols should be 0 (due to commutation).
    
    # 2. Gaussian elimination on mat_z (rows 0-25).
    # We want to clear cols 10-35.
    # We only touch cols 10-35.
    
    for r in range(26):
        # Row r of mat_z corresponds to stabilizer 10+r.
        # We want to map it to Z_{10+r}.
        # Target column is 10+r.
        target_col = 10 + r
        
        # Find pivot in mat_z[r, j] for j >= target_col.
        pivot_col = -1
        for j in range(target_col, num_qubits):
            if mat_z[r, j] == 1:
                pivot_col = j
                break
                
        if pivot_col == -1:
            print(f"Error: Z matrix rank < 26 at row {r}")
            return
            
        op_swap(target_col, pivot_col)
        
        # Clear other entries in row r (cols 10-35)
        # We use Z-logic: CNOT(target, source) adds Z_target to Z_source.
        # Wait, earlier I said:
        # CNOT(c, t): Z_t -> Z_c Z_t.
        # To clear Z in col j (make it 0) using pivot at target_col (which is 1):
        # We need Z_j -> Z_j + Z_target.
        # This means CNOT(target, j)?
        # CNOT(c, t): Z_t -> Z_t + Z_c.
        # So yes, CNOT(target, j) adds Z_target to Z_j.
        # target_col is control, j is target.
        
        for j in range(10, num_qubits):
            if j != target_col and mat_z[r, j] == 1:
                op_cnot(target_col, j)
                
    # Now mat_x = [I | 0], mat_z = [0 | I].
    # State is stabilized by X_0..X_9 and Z_10..Z_35.
    # Ops V transform S -> Canonical.
    # |psi> = V^dagger |Canonical>.
    # |Canonical> = |+>^{10} |0>^{26}.
    
    # Build circuit
    c = stim.Circuit()
    
    # 1. Prepare Canonical state
    for i in range(10):
        c.append("H", [i])
        
    # 2. Apply V^dagger.
    # Ops list has (gate, args).
    # Reverse order.
    # Inverse of SWAP is SWAP.
    # Inverse of CX(c, t) is CX(c, t).
    
    for gate, args in reversed(ops):
        c.append(gate, args)
        
    # Output
    print("CIRCUIT_START")
    print(c)
    print("CIRCUIT_END")

if __name__ == "__main__":
    solve()
