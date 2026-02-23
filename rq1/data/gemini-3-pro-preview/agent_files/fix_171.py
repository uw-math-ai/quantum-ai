import stim
import sys

def find_correction(circuit_file, stabilizers_file, output_circuit_file):
    with open(circuit_file, 'r') as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    with open(stabilizers_file, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f.readlines() if line.strip()]
    
    targets = []
    for s in lines:
        if len(s) < 171: s += 'I' * (171 - len(s))
        elif len(s) > 171: s = s[:171]
        targets.append(stim.PauliString(s))
        
    print(f"Targets: {len(targets)}")
    
    # We need to find a Pauli string C such that C anti-commutes with the failed stabilizers
    # AND commutes with the passed stabilizers?
    # No.
    # Let the current state be |psi>.
    # For each target T_i, <psi|T_i|psi> = s_i \in {+1, -1}.
    # We want s_i = +1.
    # If s_i = -1, we want to apply an operator C that flips T_i.
    # {C, T_i} = 0.
    # But C must NOT flip T_j where s_j is already +1.
    # So [C, T_j] = 0 for all j where s_j = +1.
    # And {C, T_k} = 0 for all k where s_k = -1?
    # If we apply C, it flips the sign of all T that anticommute with it.
    
    # We want to find C such that for all i:
    # If s_i = -1, {C, T_i} = 0.
    # If s_i = +1, [C, T_i] = 0.
    # This is a system of linear equations over GF(2).
    # Variables: C = X^a Z^b (2n bits).
    # Constraints: Commutation with T_i.
    # symplectic_inner_product(C, T_i) = (1 if s_i=-1 else 0).
    
    # We have 151 constraints on 342 variables.
    # We can solve this using Gaussian elimination.
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    constraints = []
    for i, t in enumerate(targets):
        exp = sim.peek_observable_expectation(t)
        desired_flip = 1 if exp == -1 else 0
        constraints.append((t, desired_flip))
        
    print(f"Solving for correction operator satisfying {len(constraints)} constraints...")
    
    # Build matrix
    # Ax = b
    # A is 151 x 342.
    # x is 342 x 1 (the correction operator C).
    # b is 151 x 1 (desired flips).
    
    # Columns of A correspond to X_0, Z_0, X_1, Z_1, ...
    # Row i is the symplectic vector of T_i (swapped X/Z because of inner product formula).
    # Commutation(A, B) = sum(Ax * Bz + Az * Bx).
    # If C = (Cx, Cz), T = (Tx, Tz).
    # Comm = Cx * Tz + Cz * Tx.
    # So if variables are (Cx_0, Cz_0, ...), the coefficients for T_i are (Tz_0, Tx_0, ...).
    
    num_qubits = 171
    num_vars = 2 * num_qubits
    
    matrix = []
    rhs = []
    
    for t, flip in constraints:
        row = []
        for k in range(num_qubits):
            # Coeff for Cx_k is Tz_k
            row.append(1 if t[k] in [2, 3] else 0) # Z or Y has Z part
            # Coeff for Cz_k is Tx_k
            row.append(1 if t[k] in [1, 2] else 0) # X or Y has X part
        matrix.append(row)
        rhs.append(flip)
        
    # Solve Ax = b using Gaussian elimination
    # We augment matrix with rhs
    
    augmented = [row + [rhs[i]] for i, row in enumerate(matrix)]
    
    # GE
    pivot_row = 0
    pivot_cols = []
    
    for col in range(num_vars):
        if pivot_row >= len(augmented): break
        
        pivot = -1
        for r in range(pivot_row, len(augmented)):
            if augmented[r][col]:
                pivot = r
                break
        
        if pivot != -1:
            augmented[pivot_row], augmented[pivot] = augmented[pivot], augmented[pivot_row]
            pivot_cols.append(col)
            
            for r in range(len(augmented)):
                if r != pivot_row and augmented[r][col]:
                    for c in range(col, len(augmented[0])):
                        augmented[r][c] ^= augmented[pivot_row][c]
            
            pivot_row += 1
            
    # Check consistency
    for r in range(pivot_row, len(augmented)):
        if augmented[r][-1] != 0:
            print("Error: Inconsistent constraints! Cannot find correction.")
            # This happens if dependent stabilizers have conflicting requirements.
            # But we generated the state by measurement, so it should be consistent with SOME sign pattern.
            # Wait, measuring T_i gives random outcome s_i.
            # If T_k = T_i * T_j, then s_k must be s_i * s_j.
            # Our constraints require flipping based on s_i.
            # If we need to flip s_i and s_j, we flip s_k = s_i * s_j => (-1)*(-1) = 1. No change.
            # But if s_k was -1, we need to flip it.
            # Is it consistent?
            # If current state |psi> has T_i -> s_i, T_j -> s_j, T_k -> s_k.
            # And T_k = T_i T_j.
            # Then s_k = s_i s_j (since they are eigenvalues).
            # We want T_i -> +1, T_j -> +1, T_k -> +1.
            # If we apply C, new signs s' satisfy s'_k = s'_i s'_j?
            # s'_i = s_i * (-1)^{comm(C, T_i)}.
            # We want s'_i = 1 => (-1)^{comm} = s_i.
            # So comm(C, T_i) = 1 if s_i = -1, else 0.
            # Consistency:
            # comm(C, T_k) = comm(C, T_i T_j) = comm(C, T_i) + comm(C, T_j).
            # Requirement:
            # target_flip(k) = target_flip(i) + target_flip(j)?
            # target_flip(k) is 1 if s_k=-1.
            # Is (s_k == -1) == (s_i == -1) XOR (s_j == -1)?
            # s_k = s_i * s_j.
            # If s_i=1, s_j=1 -> s_k=1. (0+0=0). OK.
            # If s_i=-1, s_j=1 -> s_k=-1. (1+0=1). OK.
            # If s_i=-1, s_j=-1 -> s_k=1. (1+1=0). OK.
            # Yes, it is consistent.
            return
            
    print("System solved. Extracting solution...")
    
    # Back substitution?
    # The matrix is in RREF.
    # We can set free variables to 0.
    
    solution = [0] * num_vars
    for i in range(len(pivot_cols)-1, -1, -1):
        col = pivot_cols[i]
        row = i # Because we swapped rows to match pivot_row
        
        val = augmented[row][-1]
        for c in range(col + 1, num_vars):
            if augmented[row][c]:
                val ^= solution[c]
        solution[col] = val
        
    # Convert solution to Pauli string
    correction = stim.PauliString(num_qubits)
    for k in range(num_qubits):
        cx = solution[2*k]
        cz = solution[2*k+1]
        if cx and cz: correction[k] = 'Y'
        elif cx: correction[k] = 'X'
        elif cz: correction[k] = 'Z'
        else: correction[k] = 'I'
        
    print(f"Correction operator found: {correction}")
    
    # Append correction to circuit
    # Using Pauli gates
    
    with open(output_circuit_file, 'w') as f:
        f.write(circuit_str)
        f.write("\n")
        # Apply correction
        for k in range(num_qubits):
            p = correction[k]
            if p == 1: f.write(f"X {k}\n")
            elif p == 2: f.write(f"Y {k}\n")
            elif p == 3: f.write(f"Z {k}\n")
            
    print(f"Corrected circuit written to {output_circuit_file}")

if __name__ == "__main__":
    circuit_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_171.stim"
    stabilizers_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_171.txt"
    output_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_171_corrected.stim"
    find_correction(circuit_file, stabilizers_file, output_file)
