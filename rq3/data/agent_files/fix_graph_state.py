
import stim
import sys

def solve_gf2(matrix, vector):
    """
    Solves Mx = v over GF(2) using Gaussian elimination.
    Returns x if solvable, else None.
    Matrix is a list of lists (rows).
    Vector is a list.
    """
    num_rows = len(matrix)
    if num_rows == 0:
        return []
    num_cols = len(matrix[0])
    
    # Augmented matrix
    aug = [row[:] + [val] for row, val in zip(matrix, vector)]
    
    pivot_row = 0
    pivot_cols = []
    
    for col in range(num_cols):
        if pivot_row >= num_rows:
            break
            
        # Find pivot
        pivot = -1
        for r in range(pivot_row, num_rows):
            if aug[r][col] == 1:
                pivot = r
                break
        
        if pivot != -1:
            # Swap rows
            aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
            
            # Eliminate
            for r in range(num_rows):
                if r != pivot_row and aug[r][col] == 1:
                    for c in range(col, num_cols + 1):
                        aug[r][c] ^= aug[pivot_row][c]
            
            pivot_cols.append(col)
            pivot_row += 1
    
    # Check consistency
    for r in range(pivot_row, num_rows):
        if aug[r][num_cols] == 1:
            return None # Inconsistent
            
    # Back substitution (already done mostly by Gauss-Jordan)
    solution = [0] * num_cols
    for i, col in enumerate(pivot_cols):
        solution[col] = aug[i][num_cols]
        
    return solution

def main():
    try:
        # Load circuit
        with open("candidate_graph.stim", "r") as f:
            circuit_text = f.read()
        circuit = stim.Circuit(circuit_text)
        
        # Load stabilizers
        with open("current_target_stabilizers.txt", "r") as f:
            stabilizer_lines = [line.strip() for line in f if line.strip()]
        stabilizers = [stim.PauliString(s) for s in stabilizer_lines]
        
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Simulate to find current signs
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        signs = []
        failures = 0
        zeros = 0
        for i, s in enumerate(stabilizers):
            exp = sim.peek_observable_expectation(s)
            if exp == 1:
                signs.append(0)
            elif exp == -1:
                signs.append(1)
                failures += 1
            else:
                signs.append(None) # Should not happen if eigenstate
                zeros += 1
        
        print(f"Current status: {len(signs) - failures - zeros} correct, {failures} wrong sign, {zeros} undefined (expect 0).")
        
        if zeros > 0:
            print("Error: The circuit does not stabilize some targets (expectation 0). Cannot fix with sign flips.")
            return

        if failures == 0:
            print("All signs correct! No fix needed.")
            return

        # Build matrix for correction
        # Variables: X_0, Z_0, X_1, Z_1, ... X_91, Z_91
        # 184 variables.
        num_qubits = 92
        matrix = []
        
        # We need to find P such that P anticommutes with S_k if signs[k] == 1.
        # P = Product (X_j ^ ax_j * Z_j ^ az_j)
        # S_k = Product (X_j ^ sx_kj * Z_j ^ sz_kj)
        # Anti-commutation condition: sum_j (ax_j * sz_kj + az_j * sx_kj) = 1 (mod 2)
        
        for k, s in enumerate(stabilizers):
            row = []
            for q in range(num_qubits):
                # Check contribution of X_q correction
                # X_q anticommutes with Z_q component of S_k
                # S_k on qubit q:
                # I: commutes with X, Z
                # X: commutes with X, anti with Z
                # Z: anti with X, commutes with Z
                # Y: anti with X, anti with Z
                
                pauli = s[q] # 0=I, 1=X, 2=Y, 3=Z
                
                # Coeff for X_q variable (anti with Z component of s)
                # X_q anti with Z (3) and Y (2).
                if pauli == 2 or pauli == 3:
                    row.append(1)
                else:
                    row.append(0)
                    
                # Coeff for Z_q variable (anti with X component of s)
                # Z_q anti with X (1) and Y (2).
                if pauli == 1 or pauli == 2:
                    row.append(1)
                else:
                    row.append(0)
            matrix.append(row)
            
        print("Solving linear system for corrections...")
        solution = solve_gf2(matrix, signs)
        
        if solution is None:
            print("No solution found! The signs cannot be fixed by local Paulis.")
            return
            
        print("Solution found. Appending corrections...")
        
        correction_gates = []
        for q in range(num_qubits):
            idx_x = 2 * q
            idx_z = 2 * q + 1
            if solution[idx_x] == 1:
                correction_gates.append(f"X {q}")
            if solution[idx_z] == 1:
                correction_gates.append(f"Z {q}")
                
        # Append corrections to circuit
        new_circuit = circuit.copy()
        if correction_gates:
            new_circuit.append_from_stim_program_text("\n".join(correction_gates))
            
        with open("candidate_fixed.stim", "w") as f:
            f.write(str(new_circuit))
            
        print("Saved candidate_fixed.stim")
        
        # Verify
        sim.do(stim.Circuit("\n".join(correction_gates)))
        final_failures = 0
        for s in stabilizers:
            if sim.peek_observable_expectation(s) != 1:
                final_failures += 1
        print(f"Verification: {final_failures} wrong signs remaining.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
