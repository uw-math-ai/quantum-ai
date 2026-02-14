import stim
import sys
import numpy as np

def to_check_matrix(stabs, n):
    mat = np.zeros((len(stabs), 2*n), dtype=bool)
    for i, s in enumerate(stabs):
        for k in range(n):
            # stim Pauli indexing: 0=I, 1=X, 2=Y, 3=Z
            # Check matrix standard: X part then Z part
            p = s[k]
            if p == 1 or p == 2: # X or Y
                mat[i, k] = True
            if p == 3 or p == 2: # Z or Y
                mat[i, k + n] = True
    return mat

def get_rank(stabs, n):
    if not stabs:
        return 0
    mat = to_check_matrix(stabs, n)
    rows, cols = mat.shape
    pivot_row = 0
    
    # Gaussian elimination over GF(2)
    # Convert to standard python list of lists or work with numpy
    # Numpy boolean arrays support XOR via ^
    
    for j in range(cols):
        if pivot_row >= rows:
            break
            
        # Find pivot
        pivot = -1
        for i in range(pivot_row, rows):
            if mat[i, j]:
                pivot = i
                break
                
        if pivot == -1:
            continue
            
        # Swap rows
        if pivot != pivot_row:
            mat[[pivot_row, pivot]] = mat[[pivot, pivot_row]]
            
        # Eliminate other rows
        for i in range(rows):
            if i != pivot_row and mat[i, j]:
                mat[i] ^= mat[pivot_row]
                
        pivot_row += 1
        
    return pivot_row

def solve():
    print("Reading stabilizers...")
    with open("target_stabilizers_114.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(line) for line in lines]
    n_qubits = 114
    
    print(f"Loaded {len(stabilizers)} stabilizers for {n_qubits} qubits")
    
    # Verify consistency (commutativity)
    # Checking all pairs is O(N^2), 110^2 is small enough (~12000 checks)
    for i in range(len(stabilizers)):
        for j in range(i+1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Error: Stabilizers {i} and {j} do not commute!")
                return

    print("All stabilizers commute.")

    current_stabilizers = list(stabilizers)
    current_rank = get_rank(current_stabilizers, n_qubits)
    print(f"Initial Rank: {current_rank}")
    
    if current_rank < len(current_stabilizers):
        print("Warning: Provided stabilizers are not independent.")
        # We should prune dependent ones to proceed cleanly with `from_stabilizers`?
        # Or just keep adding independent ones until we have N.
        # But if we have dependent ones, `from_stabilizers` might fail if they are inconsistent.
        # However, they come from a valid stabilizer state presumably.
        # Let's prune to a basis first.
        
        basis = []
        basis_rank = 0
        for s in current_stabilizers:
            temp = basis + [s]
            r = get_rank(temp, n_qubits)
            if r > basis_rank:
                basis.append(s)
                basis_rank = r
        
        print(f"Pruned to {len(basis)} independent stabilizers.")
        current_stabilizers = basis
    
    needed = n_qubits - len(current_stabilizers)
    print(f"Need {needed} more independent stabilizers.")
    
    # Try adding simple candidates
    candidates = []
    for q in range(n_qubits):
        # Try Z first, then X
        candidates.append(stim.PauliString("I"*q + "Z" + "I"*(n_qubits-q-1)))
        candidates.append(stim.PauliString("I"*q + "X" + "I"*(n_qubits-q-1)))
        
    added_count = 0
    for cand in candidates:
        if added_count == needed:
            break
            
        # Check commutation
        if all(cand.commutes(s) for s in current_stabilizers):
            # Check independence
            if get_rank(current_stabilizers + [cand], n_qubits) > len(current_stabilizers):
                current_stabilizers.append(cand)
                added_count += 1
                
    if len(current_stabilizers) < n_qubits:
        print(f"Failed to find enough stabilizers. Found {len(current_stabilizers)} total.")
        # If simple candidates failed, try random products?
        # But usually simple Z/X works unless the code is weird.
        return

    print(f"Completed set with {len(current_stabilizers)} stabilizers.")
    
    # Generate Tableau
    try:
        t = stim.Tableau.from_stabilizers(current_stabilizers)
        # Check if inverse is needed?
        # from_stabilizers returns a tableau T such that T|0> is stabilized by stabilizers.
        # Wait, documentation says: "Returns a Tableau that prepares the given stabilizers."
        # i.e., T * Z_k * T^-1 = stabilizer[k].
        # So the circuit is the operations in T.
        c = t.to_circuit()
        
        with open("circuit_114.stim", "w") as f:
            f.write(str(c))
        print("Circuit generated.")
        
    except Exception as e:
        print(f"Error generating tableau: {e}")

if __name__ == "__main__":
    solve()
