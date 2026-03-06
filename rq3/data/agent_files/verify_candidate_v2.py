
import stim
import sys

def get_stabilizers():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\target_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    return [stim.PauliString(l) for l in lines]

def get_candidate():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\best_candidate.stim", "r") as f:
        c = stim.Circuit(f.read())
    return c

def check_and_fix():
    stabilizers = get_stabilizers()
    circuit = get_candidate()
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    bad_indices = []
    
    for i, s in enumerate(stabilizers):
        exp = sim.peek_observable_expectation(s)
        if exp == -1:
            bad_indices.append(i)
        elif exp == 0:
            print(f"Stabilizer {i} is NOT stabilized (exp=0). Cannot fix.")
            return
            
    if not bad_indices:
        print("All stabilizers preserved.")
        return

    print(f"Bad signs for stabilizers: {bad_indices}")
    
    # Try to find a Pauli P such that P anticommutes with S[i] for i in bad_indices
    # and commutes with others.
    # We need a correction P.
    # The circuit produces state |psi>. S_i |psi> = -|psi> for i in bad.
    # We want P |psi>. S_i (P |psi>) = P (-S_i) P P^+ |psi> ? No.
    # S P |psi> = +/- P S |psi> = +/- P (-|psi>) = -/+ P |psi>.
    # So we want S P = -P S (anticommute) to flip sign.
    
    # We solve for P.
    # We can use Gaussian elimination over GF(2).
    # But checking 49 qubits is fast.
    # We can try to construct P iteratively?
    # Or just use the fact that we have a tableau.
    
    # Actually, stim has a method for this?
    # Not directly exposed as "fix signs".
    
    # Let's try to brute force single-qubit Paulis?
    # Unlikely to work if high weight.
    
    # Better: Use the tableau inverse.
    # The circuit implements a unitary U.
    # We have U |0> = |psi>.
    # We want U' |0> = |psi'> where |psi'> has correct signs.
    # Maybe simply appending X gates to the circuit is enough?
    # X_k flips signs of Z-type stabilizers on k.
    # Z_k flips signs of X-type stabilizers on k.
    
    # Let's form the matrix A where A_ij = Commute(P_j, S_i).
    # We want A x = target_flips.
    # P_j are the single qubit X and Z operators.
    # There are 2N variables.
    
    num_qubits = len(stabilizers[0])
    
    # Build matrix
    # Rows: stabilizers
    # Cols: X_0, Z_0, X_1, Z_1, ...
    # Entries: 1 if anticommutes, 0 if commutes.
    
    matrix = []
    for s in stabilizers:
        row = []
        for q in range(num_qubits):
            # Anti-commutes with X_q?
            # s has X (commute), Y (anti), Z (anti), I (commute)
            # No.
            # X_q anti-commutes with Z_q and Y_q.
            # Z_q anti-commutes with X_q and Y_q.
            
            op = s[q] # 0=I, 1=X, 2=Y, 3=Z
            
            # X_q
            if op == 2 or op == 3: # Y or Z
                row.append(1)
            else:
                row.append(0)
                
            # Z_q
            if op == 1 or op == 2: # X or Y
                row.append(1)
            else:
                row.append(0)
        matrix.append(row)
        
    # Target vector
    target = [0] * len(stabilizers)
    for i in bad_indices:
        target[i] = 1
        
    # Solve A x = target
    # Use simple Gaussian elimination
    
    # Transpose to solve x A^T = target^T ?
    # A x = target.
    # Need to implement GE.
    
    m = len(matrix) # constraints
    n = len(matrix[0]) # variables
    
    # Augmented matrix
    aug = [row[:] + [target[i]] for i, row in enumerate(matrix)]
    
    # Solve
    pivot_row = 0
    pivot_cols = []
    
    for col in range(n):
        if pivot_row >= m:
            break
            
        # Find pivot
        pivot = -1
        for r in range(pivot_row, m):
            if aug[r][col] == 1:
                pivot = r
                break
        
        if pivot == -1:
            continue
            
        # Swap
        aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
        
        # Eliminate
        for r in range(m):
            if r != pivot_row and aug[r][col] == 1:
                for c in range(col, n + 1):
                    aug[r][c] ^= aug[pivot_row][c]
                    
        pivot_cols.append(col)
        pivot_row += 1

    # Check consistency
    for r in range(pivot_row, m):
        if aug[r][n] == 1:
            print("System inconsistent. Cannot fix signs with Pauli corrections.")
            return

    # Back substitution (already done by full elimination above?)
    # If full elimination, the pivot columns have a single 1.
    # We can just set x[col] = aug[row][n].
    # Free variables can be 0.
    
    solution = [0] * n
    current_row = 0
    for col in range(n):
        if current_row < m and aug[current_row][col] == 1:
             # This is a pivot column
             solution[col] = aug[current_row][n]
             current_row += 1
             
    # Construct correction P
    correction = stim.Circuit()
    for q in range(num_qubits):
        # x_idx = 2*q for X_q, 2*q+1 for Z_q
        x_comp = solution[2*q]
        z_comp = solution[2*q+1]
        
        if x_comp and z_comp:
            correction.append("Y", [q])
        elif x_comp:
            correction.append("X", [q])
        elif z_comp:
            correction.append("Z", [q])
            
    print("Found correction!")
    # Append correction to circuit
    # Apply P after circuit to flip signs
    fixed_circuit = circuit + correction
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\best_candidate.stim", "w") as f:
        f.write(str(fixed_circuit))
        
    print("Saved fixed circuit.")

if __name__ == "__main__":
    check_and_fix()
