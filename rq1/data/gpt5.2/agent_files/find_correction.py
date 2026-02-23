import stim
import numpy as np

def find_correction():
    # Load stabilizers
    with open("stabilizers_54_v2.txt", "r") as f:
        stabilizers = [stim.PauliString(s.strip()) for s in f if s.strip()]
        
    num_qubits = 54
    num_stabs = len(stabilizers)
    print(f"Num stabilizers: {num_stabs}")
    
    # We want a Pauli string P such that {P, S_15} = 0 and [P, S_j] = 0 for j != 15.
    target_vector = np.zeros(num_stabs, dtype=int)
    target_vector[15] = 1 # We want anticommutation with S_15
    
    # Build check matrix M (num_stabs x 2*num_qubits)
    # Columns 0..n-1 are X, n..2n-1 are Z.
    M = np.zeros((num_stabs, 2 * num_qubits), dtype=int)
    for i, s in enumerate(stabilizers):
        for q in range(num_qubits):
            p = s[q]
            if p == 1: # X
                M[i, q] = 1
            elif p == 2: # Y (X and Z)
                M[i, q] = 1
                M[i, q + num_qubits] = 1
            elif p == 3: # Z
                M[i, q + num_qubits] = 1
                
    # We need v such that M * Omega * v = target_vector (mod 2)
    # Omega is symplectic form matrix: [[0, I], [I, 0]]
    # M_symp = M * Omega = [M_Z, M_X]
    M_symp = np.hstack((M[:, num_qubits:], M[:, :num_qubits]))
    
    # Solve M_symp * v = target_vector over GF(2)
    # We can use Gaussian elimination.
    # Augment matrix with target vector.
    A = np.hstack((M_symp, target_vector.reshape(-1, 1)))
    # Wait, we want v. M_symp is (50 x 108). v is (108 x 1).
    # System is usually underdetermined (many solutions).
    # We can use pseudoinverse or just Gaussian elimination on the transposed system?
    # No, simple Gaussian elimination.
    # However, numpy doesn't do GF(2).
    # We can implement a simple solver.
    
    # But wait, stim has tableau logic which is efficient.
    # Can we just use tableau?
    # Tableau has `z_output` which are the destabilizers (Wait, no).
    # Tableau has `x_output` and `z_output`.
    # `z_output` corresponds to the stabilizers (generators).
    # `x_output` corresponds to the destabilizers (operators that anticommute with corresponding z_output and commute with others).
    # So if we find the index k such that `z_output[k] == stabilizers[15]`, then `x_output[k]` is our correction operator P!
    
    t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    
    # Find which output generator matches S_15
    target_s = stabilizers[15]
    match_index = -1
    
    # Check z_outputs
    # Note: from_stabilizers might reorder or mix them?
    # It might do Gaussian elimination to simplify generators.
    # So `z_output` might not match `stabilizers` one-to-one.
    # We need to express S_15 as product of `z_output`s?
    # No, we need an operator that anticommutes with S_15.
    # If S_15 = product(Z_i), then any operator anticommuting with S_15 must anticommute with an odd number of Z_i.
    # This is getting complicated.
    
    # Let's stick to the linear algebra approach.
    # It's robust.
    
    # Implement GF(2) solver
    # We want to solve M_symp * v = target
    # M_symp is 50 x 108.
    # Use standard Gaussian elimination.
    
    m, n = M_symp.shape
    aug = np.hstack((M_symp, target_vector.reshape(-1, 1)))
    
    # Forward elimination
    pivot_row = 0
    pivots = []
    for col in range(n):
        if pivot_row >= m:
            break
        
        # Find pivot
        rows = np.where(aug[pivot_row:, col] == 1)[0]
        if len(rows) == 0:
            continue
            
        pivot = rows[0] + pivot_row
        
        # Swap rows
        aug[[pivot_row, pivot]] = aug[[pivot, pivot_row]]
        
        # Eliminate below
        for r in range(pivot_row + 1, m):
            if aug[r, col] == 1:
                aug[r] ^= aug[pivot_row]
                
        pivots.append((pivot_row, col))
        pivot_row += 1
        
    # Back substitution? No, we need to check consistency.
    # If any row is all zeros but augmented part is 1, then no solution.
    for r in range(pivot_row, m):
        if aug[r, -1] == 1:
            print("No solution found! The failing stabilizer is dependent on others.")
            return None

    # If consistent, find a solution.
    # Free variables can be set to 0.
    # Pivot variables are determined by back substitution.
    v = np.zeros(n, dtype=int)
    
    for r, c in reversed(pivots):
        val = aug[r, -1]
        # Subtract contributions from already set variables (to the right)
        # In GF(2), subtraction is XOR.
        # Check dot product of row r with v (only cols > c matters)
        dot = np.dot(aug[r, c+1:-1], v[c+1:]) % 2
        v[c] = val ^ dot
        
    # Convert v to Pauli string
    # v is [Z_part, X_part] because M_symp = [M_Z, M_X]
    # Wait, M_symp cols 0..n-1 correspond to Z part of P?
    # M_symp * v = (M_Z * v_Z + M_X * v_X)
    # Symplectic product: P1=(X1,Z1), P2=(X2,Z2). P1*P2 = X1 Z2 + Z1 X2.
    # Here M is (X_S, Z_S). We want (X_S Z_P + Z_S X_P) = 1.
    # M_symp = [Z_S, X_S].
    # So v must be [X_P, Z_P].
    # So first 54 elements of v are X components of P.
    # Next 54 elements are Z components.
    
    xs = v[:num_qubits]
    zs = v[num_qubits:]
    
    pauli_str = ""
    for i in range(num_qubits):
        x = xs[i]
        z = zs[i]
        if x and z:
            pauli_str += "Y"
        elif x:
            pauli_str += "X"
        elif z:
            pauli_str += "Z"
        else:
            pauli_str += "I"
            
    print(f"Correction Pauli string: {pauli_str}")
    
    # Verify it works
    P = stim.PauliString(pauli_str)
    # Check anticommutation with S_15
    if P.commutes(stabilizers[15]):
        print("ERROR: Commutes with S_15!")
    else:
        print("OK: Anticommutes with S_15.")
        
    # Check commutation with others
    for i, s in enumerate(stabilizers):
        if i == 15: continue
        if not P.commutes(s):
            print(f"ERROR: Anticommutes with S_{i}!")
            
    # Save to file
    with open("correction_op.txt", "w") as f:
        f.write(pauli_str)

if __name__ == "__main__":
    find_correction()
