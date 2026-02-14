import stim
import numpy as np

def solve():
    # Stabilizers
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
    
    all_stabilizers = x_stabilizers + z_stabilizers
    print(f"Number of stabilizers: {len(all_stabilizers)}")
    
    # Check if they are independent
    # Construct a check matrix
    # 20 rows, 72 columns (36 X, 36 Z)
    
    num_qubits = 36
    matrix = np.zeros((len(all_stabilizers), 2 * num_qubits), dtype=int)
    
    for i, stab in enumerate(all_stabilizers):
        for q, char in enumerate(stab):
            if char == 'X':
                matrix[i, q] = 1
            elif char == 'Z':
                matrix[i, num_qubits + q] = 1
            elif char == 'Y':
                matrix[i, q] = 1
                matrix[i, num_qubits + q] = 1
                
    # Check rank
    # Simple Gaussian elimination
    
    def rank(mat):
        m = mat.copy()
        rows, cols = m.shape
        pivot_row = 0
        for col in range(cols):
            if pivot_row >= rows:
                break
            # Find a row with a 1 in this column
            swap_row = -1
            for r in range(pivot_row, rows):
                if m[r, col] == 1:
                    swap_row = r
                    break
            
            if swap_row != -1:
                # Swap rows
                m[[pivot_row, swap_row]] = m[[swap_row, pivot_row]]
                
                # Eliminate other rows
                for r in range(rows):
                    if r != pivot_row and m[r, col] == 1:
                        m[r] ^= m[pivot_row]
                
                pivot_row += 1
                
        return pivot_row

    r = rank(matrix)
    print(f"Rank of stabilizer matrix: {r}")
    if r < len(all_stabilizers):
        print("Stabilizers are not independent!")
    
    if r < num_qubits:
        print(f"Underconstrained system! Rank {r} < {num_qubits} qubits.")
        # We need 36 independent stabilizers for a pure state.
        # If we have fewer, it's a mixed state or we need to add more stabilizers?
        # The problem asks for "the stabilizer state defined by these generators".
        # Usually implies these are the generators of the stabilizer group.
        # If the group has size < 36, it defines a subspace.
        # "The final quantum state ... must be a +1 eigenstate of every provided stabilizer generator."
        # This implies any state in the subspace is fine?
        # Usually "stabilizer state" implies a unique state (rank = n).
        # Let's see if I missed any.
        
        # Maybe there are implicit stabilizers?
        # Or maybe I should complete the set?
        pass

if __name__ == "__main__":
    solve()
