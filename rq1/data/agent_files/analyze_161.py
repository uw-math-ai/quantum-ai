import sys
import numpy as np

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        # Filter out empty lines and comments
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    
    if not lines:
        print("No stabilizers found in file")
        return None, 0

    # Check dimensions
    num_stabilizers = len(lines)
    num_qubits = len(lines[0])
    
    print(f"Number of stabilizers: {num_stabilizers}")
    print(f"Number of qubits: {num_qubits}")
    
    # Create binary matrix [X | Z]
    tableau = np.zeros((num_stabilizers, 2 * num_qubits), dtype=int)
    
    for i, line in enumerate(lines):
        if len(line) != num_qubits:
             print(f"Error: Stabilizer {i} has length {len(line)}, expected {num_qubits}")
             return None, num_qubits
             
        for j, char in enumerate(line):
            if char == 'X':
                tableau[i, j] = 1
            elif char == 'Z':
                tableau[i, j + num_qubits] = 1
            elif char == 'Y':
                tableau[i, j] = 1
                tableau[i, j + num_qubits] = 1
            elif char == 'I':
                pass
            else:
                raise ValueError(f"Unknown character {char} in stabilizer {i}")
                
    return tableau, num_qubits

if __name__ == "__main__":
    tableau, n = parse_stabilizers("stabilizers_161.txt")
    
    if tableau is None:
        sys.exit(1)

    # Check commutativity
    x_part = tableau[:, :n]
    z_part = tableau[:, n:]
    
    commutator_matrix = (np.matmul(x_part, z_part.T) + np.matmul(z_part, x_part.T)) % 2
    
    non_commuting_count = np.sum(commutator_matrix) / 2 # /2 because it's symmetric
    print(f"Number of non-commuting pairs: {non_commuting_count}")

    if non_commuting_count == 0:
        print("All stabilizers commute.")
    else:
        print("Stabilizers do NOT commute.")
        
    # Standard Gaussian elimination
    def row_reduce(mat):
        m = mat.copy()
        rows, cols = m.shape
        pivot_row = 0
        for col in range(cols):
            if pivot_row >= rows:
                break
            if m[pivot_row, col] == 0:
                swap_row = -1
                for r in range(pivot_row + 1, rows):
                    if m[r, col] == 1:
                        swap_row = r
                        break
                if swap_row != -1:
                    m[[pivot_row, swap_row]] = m[[swap_row, pivot_row]]
                else:
                    continue 
            
            for r in range(rows):
                if r != pivot_row and m[r, col] == 1:
                    m[r] = (m[r] + m[pivot_row]) % 2
            
            pivot_row += 1
        return m, pivot_row

    rref, rank = row_reduce(tableau)
    print(f"Rank of stabilizer matrix: {rank}")
