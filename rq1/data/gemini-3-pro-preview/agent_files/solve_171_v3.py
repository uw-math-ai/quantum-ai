import stim
import sys
import os

def to_binary(paulis):
    # paulis is list of stim.PauliString
    # Returns matrix of bools
    if not paulis: return []
    num_qubits = len(paulis[0])
    rows = []
    for p in paulis:
        row = []
        # X part (X=1, Y=2 have X component)
        for k in range(num_qubits):
            # p[k] returns 0=I, 1=X, 2=Y, 3=Z
            val = p[k]
            row.append(val == 1 or val == 2)
        # Z part (Y=2, Z=3 have Z component)
        for k in range(num_qubits):
            val = p[k]
            row.append(val == 2 or val == 3)
        rows.append(row)
    return rows

def gaussian_elimination(rows):
    # rows is list of list of bools
    # Returns rank
    # Standard Gaussian elimination over GF(2)
    if not rows: return 0
    num_cols = len(rows[0])
    mat = [r[:] for r in rows] # copy
    rank = 0
    pivot_row = 0
    
    for col in range(num_cols):
        if pivot_row >= len(mat): break
        
        # Find pivot
        pivot = -1
        for r in range(pivot_row, len(mat)):
            if mat[r][col]:
                pivot = r
                break
        
        if pivot != -1:
            # Swap
            mat[pivot_row], mat[pivot] = mat[pivot], mat[pivot_row]
            
            # Eliminate
            for r in range(len(mat)):
                if r != pivot_row and mat[r][col]:
                    # XOR
                    for c in range(col, num_cols):
                        mat[r][c] = mat[r][c] ^ mat[pivot_row][c]
            
            rank += 1
            pivot_row += 1
            
    return rank

def solve_stabilizers(stabilizers_file, output_file):
    with open(stabilizers_file, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f.readlines() if line.strip()]
    
    stabilizers = []
    for i, s in enumerate(lines):
        if len(s) < 171:
            s = s + 'I' * (171 - len(s))
        elif len(s) > 171:
            s = s[:171]
        ps = stim.PauliString(s)
        if len(ps) != 171:
            print(f"Error: Stabilizer {i} has length {len(ps)}")
        stabilizers.append(ps)
    
    if not stabilizers:
        print("No stabilizers loaded.")
        return
        
    n = len(stabilizers[0]) # 171
    print(f"Loaded {len(stabilizers)} stabilizers for {n} qubits.")
    
    # Filter base stabilizers for independence
    print("Filtering base stabilizers for independence...")
    independent_stabilizers = []
    
    current_binary_rows = []
    current_rank = 0
    
    for s in stabilizers:
        row = to_binary([s])[0]
        test_rows = current_binary_rows + [row]
        new_rank = gaussian_elimination(test_rows)
        if new_rank > current_rank:
            independent_stabilizers.append(s)
            current_binary_rows.append(row)
            current_rank = new_rank
            
    print(f"Independent base stabilizers: {len(independent_stabilizers)} (Rank: {current_rank})")
    
    current_stabilizers = independent_stabilizers.copy()
    
    def try_add_candidate(cand, row):
        nonlocal current_rank
        # Check commutativity first
        for s in current_stabilizers:
            if not s.commutes(cand):
                return False
        
        # Check independence
        test_rows = current_binary_rows + [row]
        new_rank = gaussian_elimination(test_rows)
        
        if new_rank > current_rank:
            current_stabilizers.append(cand)
            current_binary_rows.append(row)
            current_rank = new_rank
            return True
        return False
    
    # Try Z_k
    for k in range(n):
        if len(current_stabilizers) == n:
            break
        # Z_k binary
        row = [False]*n + [False]*n
        row[n+k] = True
        cand = stim.PauliString(n)
        cand[k] = 'Z'
        try_add_candidate(cand, row)

    # Try X_k
    if len(current_stabilizers) < n:
        for k in range(n):
            if len(current_stabilizers) == n:
                break
            # X_k binary
            row = [False]*n + [False]*n
            row[k] = True
            cand = stim.PauliString(n)
            cand[k] = 'X'
            try_add_candidate(cand, row)

    # Try Y_k
    if len(current_stabilizers) < n:
        for k in range(n):
            if len(current_stabilizers) == n:
                break
            # Y_k binary (X=1, Z=1)
            row = [False]*n + [False]*n
            row[k] = True
            row[n+k] = True
            cand = stim.PauliString(n)
            cand[k] = 'Y'
            try_add_candidate(cand, row)
            
    # Try Random
    if len(current_stabilizers) < n:
        print("Trying random candidates...")
        for _ in range(1000):
            if len(current_stabilizers) == n:
                break
            cand = stim.PauliString.random(n)
            row = to_binary([cand])[0]
            if try_add_candidate(cand, row):
                print(f"Added Random")

    print(f"Total stabilizers: {len(current_stabilizers)}")

    print(f"Total stabilizers: {len(current_stabilizers)}")
    
    if len(current_stabilizers) == n:
        try:
            tableau = stim.Tableau.from_stabilizers(current_stabilizers)
            circuit = tableau.to_circuit(method="elimination")
            with open(output_file, "w") as f:
                f.write(str(circuit))
            print(f"Circuit written to {output_file}")
        except Exception as e:
            print(f"Error creating tableau: {e}")
    else:
        print("Failed to complete the set.")

if __name__ == "__main__":
    stabilizers_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_171.txt"
    output_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_171.stim"
    solve_stabilizers(stabilizers_file, output_file)
