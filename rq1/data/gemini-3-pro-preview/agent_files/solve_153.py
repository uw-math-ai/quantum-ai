import stim
import sys

def solve():
    # Read stabilizers
    with open(r'data\gemini-3-pro-preview\agent_files\stabilizers_153_extracted.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Validate length
    n_qubits = len(stabilizers[0])
    print(f"Number of qubits (from first): {n_qubits}")
    
    for i, s in enumerate(stabilizers):
        if len(s) != n_qubits:
            print(f"Stabilizer {i} has length {len(s)}")
            
    # If lengths differ, we have a problem.
    # From the error, at least one has length 151.
    # The prompt says 153 qubits.
    # Stabilizers should be length 153.
    # If they are 151, maybe they are missing II at the end or beginning?
    # Or maybe n_qubits should be 153 regardless of the first line?
    
    n_qubits = 153
    print(f"Target qubits: {n_qubits}")

    
    # Create a Tableau from the stabilizers
    # We want to find a circuit that prepares the state stabilized by these operators.
    # Stim's Tableau.from_stabilizers can do this if we have a full set of N stabilizers.
    # If we have fewer than N, we can pad with Z operators on the remaining degrees of freedom
    # (assuming they are logical qubits), or just pick *any* state that satisfies them.
    # However, the problem statement implies these are generators.
    # If there are fewer than 153, we have logical qubits.
    # Let's count them.
    print(f"Number of stabilizers: {len(stabilizers)}")

    # We can try to use stim.Tableau.from_stabilizers
    # But it requires a full set of commuting stabilizers for a stabilizer state.
    # If the provided list is incomplete (under-constrained), we need to complete it.
    # If it's over-complete (redundant), we need to select a basis.
    # If it's inconsistent, we have a problem.

    # Let's try to construct a tableau.
    # We can use the Gaussian elimination approach.
    # We will build a tableau where the Z stabilizers are the given stabilizers.
    # If we have < N stabilizers, we can fill the rest with arbitrary Pauli Z's that commute with everything
    # and are independent.
    # Actually, we can just use Stim to help us.
    
    # Check for consistency and independence first?
    # No, let's just use stim.TableauSimulator? No that simulates a circuit.
    
    # Algorithm:
    # 1. Create a tableau with rows corresponding to the stabilizers.
    #    (Since we are preparing |0> -> State, this is equivalent to finding a Clifford C such that
    #     C * Z_i * C^dag = S_i for all i)
    #    This is not quite right. We want the state |psi> such that S_i |psi> = |psi>.
    #    If we find a tableau T such that its Z outputs are the S_i, then T applied to |0> gives |psi>.
    
    # Stim's Tableau class allows `from_stabilizers` but expects a list of n stabilizers.
    # Let's see if we have 153.
    
    # If we have 152 stabilizers for 153 qubits, we need to find one more.
    # The last stabilizer must commute with all 152 existing ones and be independent.
    # Since we only need *a* state, we can pick any valid completion.
    
    # We can try to append Z_i for each qubit i and see if it works.
    # But checking independence is hard without Gaussian elimination.
    # Let's use stim's Tableau properties.
    
    # If we convert the stabilizers to a tableau, we can see which qubits are "stabilized".
    # But we can't make a Tableau from incomplete stabilizers directly.
    
    # Alternative:
    # 1. Represent stabilizers as a boolean matrix (check matrix).
    # 2. Perform Gaussian elimination to find the "destabilizers" or just finding independence.
    
    # Let's try a simpler approach:
    # Try adding Z_0. If it commutes with all, and is independent, good.
    # Independence check:
    #   Form a list of 153 stabilizers (152 + candidate).
    #   Check if stim.Tableau.from_stabilizers works.
    
    # If no single qubit operator works, we need to find a logical operator.
    # We can use Gaussian elimination on the check matrix.
    
    # Construct check matrix
    # Shape: (152, 2*n_qubits)
    # Columns: X_0...X_{n-1}, Z_0...Z_{n-1}
    # But Stim's Tableau Simulator can do this via `stim.Tableau.from_stabilizers` if we had n.
    # We can use the internal tableau logic or just raw numpy/scipy if available?
    # No, let's implement Gaussian elimination over GF(2) ourselves or use a library?
    # Stim has no public linear algebra for this.
    
    # Let's try to find a logical operator by brute force? No, 2^153 is too big.
    # But we can build the matrix and solve H * x = 0 (mod 2) where * is symplectic product.
    
    # Wait, we can use `stim.Tableau.from_stabilizers` with `allow_underconstrained=True`?
    # No such parameter.
    
    # Let's try this:
    # Use `stim.Tableau.from_parity_check_matrix`? No.
    
    # We'll implement a simple Gaussian elimination to find the kernel.
    # Each stabilizer is a row of 2n bits.
    # X part: bits 0..n-1
    # Z part: bits n..2n-1
    
    import numpy as np
    
    def to_check_vector(s, n):
        # s is a stim.PauliString
        vec = np.zeros(2*n, dtype=int)
        for i in range(n):
            p = s[i]
            if p == 1 or p == 2: # X or Y
                vec[i] = 1 # X component
            if p == 3 or p == 2: # Z or Y
                vec[n+i] = 1 # Z component
        return vec
        
    existing_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    check_matrix = np.array([to_check_vector(s, n_qubits) for s in existing_stabilizers], dtype=int)
    
    # We need to find v such that check_matrix * Omega * v = 0
    # Omega is the symplectic form block matrix:
    # [0 I]
    # [I 0]
    # So v_x * Z_row + v_z * X_row = 0 for each row.
    
    # Let H be the check matrix.
    # We want v such that H_x * v_z + H_z * v_x = 0
    # Let's rewrite as a standard linear system over GF(2).
    # Concatenate [H_z | H_x] as the matrix A.
    # We solve A * [v_x; v_z] = 0.
    
    H_x = check_matrix[:, :n_qubits]
    H_z = check_matrix[:, n_qubits:]
    A = np.hstack((H_z, H_x))
    
    # Now solve A x = 0 over GF(2).
    # We can use Gaussian elimination.
    # A is 152 x 306.
    # Kernel dimension should be 306 - rank(A).
    # Since stabilizers are independent, rank(A) = 152.
    # Kernel dim = 154.
    # The kernel contains the rows of [H_x | H_z] (the stabilizers themselves).
    # We want a solution that is NOT in the span of the stabilizers.
    
    # How to check if a solution is in the span of stabilizers?
    # The stabilizers correspond to vectors [v_x; v_z] in the kernel.
    # Wait, the stabilizers are vectors in the full space 2n.
    # The condition "commutes with all stabilizers" means being in the kernel of the symplectic form defined by the stabilizers.
    # The stabilizers are isotropic (commute with themselves), so they are in their own kernel.
    
    # So we have a space S (stabilizers).
    # We found S_perp (the kernel of the commutation relations).
    # We know S <= S_perp.
    # We want to pick v in S_perp such that v is not in S.
    # Then we add v to our stabilizers.
    
    # Let's perform Gaussian elimination on A to find a basis for the kernel.
    # We'll get 154 basis vectors.
    # We need to check which one is not in S.
    
    # However, simpler:
    # Just find ONE vector v that commutes with all rows.
    # Check if v is independent of rows.
    # If yes, done.
    
    # To implement:
    # 1. Transpose A to (306, 152).
    # 2. Gaussian eliminate to get RREF.
    # 3. Read off the kernel basis.
    
    # Or just use a random vector v, project it onto the kernel?
    # No, that's for vector spaces with inner products.
    
    # Let's implement RREF over GF(2).
    
    def rref(matrix):
        m = matrix.copy()
        rows, cols = m.shape
        pivot_row = 0
        pivot_cols = []
        
        # Keep track of pivot rows for back-substitution or simply use the fact it's RREF
        
        for c in range(cols):
            if pivot_row >= rows:
                break
            
            # Find pivot
            pivot = -1
            for r in range(pivot_row, rows):
                if m[r, c] == 1:
                    pivot = r
                    break
            
            if pivot == -1:
                continue
            
            pivot_cols.append(c)
            
            # Swap
            if pivot != pivot_row:
                m[[pivot, pivot_row]] = m[[pivot_row, pivot]]
                
            # Eliminate
            for r in range(rows):
                if r != pivot_row and m[r, c] == 1:
                    m[r] ^= m[pivot_row]
            
            pivot_row += 1
            
        return m, pivot_cols

    # Compute kernel of A
    # A is (152, 306).
    # RREF of A.
    rref_A, pivots = rref(A)
    
    # Free variables are columns not in pivots.
    free_cols = [c for c in range(A.shape[1]) if c not in pivots]
    
    # Construct basis for kernel.
    # For each free column k, set x_k = 1, other free vars = 0.
    # Then solve for pivot vars.
    # But since it's RREF, the pivot vars are just determined by the free vars.
    # Specifically, for each row i (corresponding to pivot col p_i),
    # x_{p_i} + sum_{j in free} M_{i,j} x_j = 0
    # => x_{p_i} = sum_{j in free} M_{i,j} x_j
    
    kernel_basis = []
    
    # We just need ONE vector that is not a stabilizer.
    # Let's try the first few kernel basis vectors.
    
    # Map from pivot col index to row index in RREF
    pivot_col_to_row = {p: i for i, p in enumerate(pivots)} # pivot_cols is correct here
    
    for free_c in free_cols:
        vec = np.zeros(A.shape[1], dtype=int)
        vec[free_c] = 1
        
        # For each pivot variable, determine its value
        for p in pivots:
            row_idx = pivot_col_to_row[p]
            if rref_A[row_idx, free_c] == 1:
                vec[p] = 1
        
        kernel_basis.append(vec)
        
    print(f"Kernel dimension: {len(kernel_basis)}")
    
    # Convert kernel basis vectors to PauliStrings and check independence against stabilizers.
    # Each vec is [v_x, v_z].
    # Stabilizers are [H_x, H_z] but in A we used [H_z, H_x].
    # So vec corresponds to [v_x, v_z].
    # PauliString has X where v_x=1, Z where v_z=1.
    
    potential_logicals = []
    for vec in kernel_basis:
        v_x = vec[:n_qubits]
        v_z = vec[n_qubits:]
        
        # Construct PauliString
        p_str = ""
        for i in range(n_qubits):
            x = v_x[i]
            z = v_z[i]
            if x and z:
                p_str += "Y"
            elif x:
                p_str += "X"
            elif z:
                p_str += "Z"
            else:
                p_str += "I"
        
        p = stim.PauliString(p_str)
        potential_logicals.append(p)
        
    print(f"Found {len(potential_logicals)} kernel basis vectors.")
    
    # Now check which one is independent.
    # We can try to add them one by one.
    
    for cand in potential_logicals:
        try:
            full_set = existing_stabilizers + [cand]
            t = stim.Tableau.from_stabilizers(full_set)
            print(f"Success! Added logical operator: {cand}")
            
            circuit = t.to_circuit()
            with open(r'data\gemini-3-pro-preview\agent_files\circuit_153.stim', 'w') as out:
                out.write(str(circuit))
            return
        except ValueError:
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue

    print("Failed to find independent logical operator.")

    
if __name__ == "__main__":
    solve()
