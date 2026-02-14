import stim
import numpy as np
import galois
import sys

def solve():
    print("Reading stabilizers...")
    with open('target_stabilizers_186.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    n_qubits = 186
    num_provided = len(stabilizers)
    print(f"Loaded {num_provided} stabilizers for {n_qubits} qubits.")
    
    if num_provided > n_qubits:
        print("Error: Too many stabilizers provided.")
        return

    # Convert to GF(2) matrix
    GF = galois.GF(2)
    
    # Each stabilizer is a row: [X1..Xn Z1..Zn]
    matrix = np.zeros((num_provided, 2 * n_qubits), dtype=int)
    
    for i, s in enumerate(stabilizers):
        if len(s) != n_qubits:
            print(f"Error: Stabilizer {i} length {len(s)} != {n_qubits}")
            return
        for j, char in enumerate(s):
            if char == 'X':
                matrix[i, j] = 1
            elif char == 'Z':
                matrix[i, j + n_qubits] = 1
            elif char == 'Y':
                matrix[i, j] = 1
                matrix[i, j + n_qubits] = 1
                
    gf_matrix = GF(matrix)
    
    # Check rank
    rank = np.linalg.matrix_rank(gf_matrix)
    print(f"Rank of provided stabilizers: {rank}")
    
    if rank < num_provided:
        print("Warning: Stabilizers are not linearly independent.")
        # We might need to select a basis, but for now let's assume they are and see.
        # If not, we should probably reduce them.
    
    # Commutation check
    # Omega matrix
    # [0 I]
    # [I 0]
    # But usually defined as symplectic inner product.
    # A * Omega * B^T = 0
    
    print("Checking commutation...")
    # Using simple numpy for commutation check to be faster? 
    # Or just trust the problem statement + my check.
    # Let's do it in logic.
    
    # We need to complete the stabilizers.
    # If rank is 182, we need 4 more.
    
    current_stabs = gf_matrix
    
    # Define Omega
    # Omega is (2n x 2n)
    # J = [[0, I], [I, 0]]
    Omega = np.zeros((2 * n_qubits, 2 * n_qubits), dtype=int)
    Omega[:n_qubits, n_qubits:] = np.eye(n_qubits, dtype=int)
    Omega[n_qubits:, :n_qubits] = np.eye(n_qubits, dtype=int)
    Omega_gf = GF(Omega)
    
    while current_stabs.shape[0] < n_qubits:
        print(f"Current stabilizers: {current_stabs.shape[0]}. Finding next...")
        
        # Calculate commutators with current stabs
        # We want v such that current_stabs * Omega * v^T = 0
        # Let A = current_stabs * Omega
        # Solve A x = 0
        
        A = current_stabs @ Omega_gf
        null_space = A.null_space() # Returns basis vectors in rows
        
        # We need a vector in null_space that is NOT in current_stabs
        # current_stabs spans the stabilizer group S
        # null_space spans the centralizer C(S)
        # We want v in C(S) \ S.
        
        found = False
        
        # To check independence efficiently:
        # We can form a matrix of [current_stabs] and try to add v
        # If rank increases, it's independent.
        
        # Check rank of current_stabs once
        current_rank = np.linalg.matrix_rank(current_stabs)
        
        # Heuristic: try vectors from the null basis
        # If null_space basis vectors are v1, v2, ...
        # Some might be in S, some outside.
        
        # Convert to numpy for faster rank check maybe? Galois is fine.
        
        for v in null_space:
            # Check if independent
            candidate = np.vstack([current_stabs, v])
            if np.linalg.matrix_rank(candidate) > current_rank:
                current_stabs = candidate
                found = True
                print(f"Found new stabilizer. Total: {current_stabs.shape[0]}")
                break
        
        if not found:
            # Try combinations if basis vectors themselves are in S (unlikely for all of them unless full)
            print("Could not find independent stabilizer in basis. Trying sum...")
            v_sum = np.sum(null_space, axis=0)
            candidate = np.vstack([current_stabs, v_sum])
            if np.linalg.matrix_rank(candidate) > current_rank:
                 current_stabs = candidate
                 found = True
                 print(f"Found new stabilizer (sum). Total: {current_stabs.shape[0]}")
            else:
                 print("Error: Could not complete stabilizer set.")
                 return

    print("Completed stabilizer set.")
    
    # Now convert back to strings for Stim
    final_stabilizers = []
    
    # We need to construct Pauli strings
    # Note: The logicals we added might have phase factors, but here we just have the Pauli operators (X/Z/Y).
    # Stim's tableau from_stabilizers assumes +1 phase if not specified?
    # Wait, stim.Tableau.from_stabilizers takes a list of PauliString.
    # If we pass "XX", it means +XX.
    # The problem requires +1 eigenstates for the *provided* generators.
    # The ones we added can be +/- 1, but "from_stabilizers" will define a state that is +1 eigenstate of the strings we pass.
    # So we effectively choose +1 for the new stabilizers too. This is fine, we just need *a* state.
    
    final_np = np.array(current_stabs, dtype=int)
    
    stim_list = []
    for i in range(n_qubits):
        row = final_np[i]
        s = ""
        for j in range(n_qubits):
            x = row[j]
            z = row[j + n_qubits]
            if x and z: s += "Y"
            elif x: s += "X"
            elif z: s += "Z"
            else: s += "I"
        stim_list.append(stim.PauliString(s))
        
    # Generate Circuit
    t = stim.Tableau.from_stabilizers(stim_list)
    c = t.to_circuit()
    
    with open('circuit_186.stim', 'w') as f:
        f.write(str(c))
    print("Circuit saved to circuit_186.stim")

if __name__ == "__main__":
    solve()
