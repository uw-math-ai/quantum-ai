import stim
import numpy as np

# Stabilizers from the prompt
stabilizers = [
    "XXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXXXXXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXXIII",
    "XXXIIIXXXIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXIIIXXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXXIIIXXXIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIIXXX",
    "ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII",
    "ZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIII",
    "IIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIII",
    "IIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIII",
    "IIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZI",
    "IIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZ",
    "XXXIIIIIIXXXIIIIIIXXXIIIIIIXXXIIIIII",
    "ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII"
]

def solve():
    num_qubits = 36
    
    # Check linear independence first
    def to_vec(s):
        x = [1 if c in 'XY' else 0 for c in s]
        z = [1 if c in 'ZY' else 0 for c in s]
        return np.concatenate([x, z])
        
    vecs = np.array([to_vec(s) for s in stabilizers])
    
    # Full check matrix of generators: 34 x 72.
    mat = vecs.copy() # 34 x 72
    
    ops = [] # (gate, args)
    
    # Since we modify mat by column operations (gates), let's track them.
    # Note: Column operations on the check matrix correspond to CONJUGATING the stabilizers by gates.
    # CNOT(c, t): X_t += X_c, Z_c += Z_t.
    # H(q): Swap X_q, Z_q.
    # S(q): Z_q += X_q. (Wait, S: X->Y, Z->Z. X_q -> X_q+Z_q? Yes).
    
    def op_swap(q1, q2):
        if q1 == q2: return
        mat[:, [q1, q2]] = mat[:, [q2, q1]]
        mat[:, [q1+num_qubits, q2+num_qubits]] = mat[:, [q2+num_qubits, q1+num_qubits]]
        ops.append(("SWAP", [q1, q2]))
        
    def op_cnot(c, t):
        if c == t: return
        # X: col c adds to col t
        mat[:, t] ^= mat[:, c]
        # Z: col t adds to col c
        mat[:, c+num_qubits] ^= mat[:, t+num_qubits]
        ops.append(("CX", [c, t]))
        
    def op_h(q):
        mat[:, [q, q+num_qubits]] = mat[:, [q+num_qubits, q]]
        ops.append(("H", [q]))
        
    def op_s(q):
        # S: X->Y, Z->Z.
        # X -> X Z
        # Z -> Z
        # So Z column gets added X column?
        # Check: Y has X=1, Z=1.
        # X=1, Z=0 -> X=1, Z=1.
        # Correct.
        mat[:, q+num_qubits] ^= mat[:, q]
        ops.append(("S", [q]))
        
    # Phase 1: Row Reduction (Gaussian elimination on rows)
    # This simplifies the GENERATOR SET but does not change the stabilizer group.
    # We can do whatever row operations we want.
    
    pivot_row = 0
    # Prefer X pivots first
    for col in range(num_qubits): 
        if pivot_row >= 34: break
        
        pivot = -1
        for r in range(pivot_row, 34):
            if mat[r, col] == 1:
                pivot = r
                break
        
        if pivot != -1:
            mat[[pivot_row, pivot]] = mat[[pivot, pivot_row]]
            for r in range(34):
                if r != pivot_row and mat[r, col] == 1:
                    mat[r] ^= mat[pivot_row]
            pivot_row += 1
            
    # If pivot_row < 34, check Z columns
    for col in range(num_qubits, 2*num_qubits):
        if pivot_row >= 34: break
        
        pivot = -1
        for r in range(pivot_row, 34):
            if mat[r, col] == 1:
                pivot = r
                break
                
        if pivot != -1:
            mat[[pivot_row, pivot]] = mat[[pivot, pivot_row]]
            for r in range(34):
                if r != pivot_row and mat[r, col] == 1:
                    mat[r] ^= mat[pivot_row]
            pivot_row += 1
            
    if pivot_row < 34:
        print(f"Warning: Rank is {pivot_row} < 34")
        # But we continue.
        
    # Phase 2: Diagonalize using Gates (Column Operations)
    # We want to make the check matrix diagonal.
    # Target: Row r has X on qubit r, and identity on other qubits (for r < 34).
    # Then we have generators X_0 ... X_33.
    # Wait, if we transform to X_0...X_33, then the state is stabilized by X_0...X_33.
    # This is |+> on 0..33, and anything on 34..35.
    # But this requires finding gates that transform original G_i to X_i.
    
    # Algorithm:
    # Iterate r from 0 to 33.
    # 1. Bring a Pauli X (or Z) to position (r, r).
    #    If mat[r, r] has X, good.
    #    If mat[r, r] has Z, apply H(r).
    #    If mat[r, r] has Y, apply S(r) then H(r) -> X. (Or just Sdag? Sdag: Y->X).
    #    Wait, Sdag Y -> X?
    #    S: X->Y. Sdag: Y->X.
    #    So apply S_dag.
    
    for r in range(34):
        # 1. Find a pivot column j >= r for row r.
        # Prefer X.
        pivot_col = -1
        pivot_type = None
        
        # Check X
        for j in range(r, num_qubits):
            if mat[r, j] == 1:
                pivot_col = j
                pivot_type = 'X'
                break
        
        # Check Z if no X
        if pivot_col == -1:
            for j in range(r, num_qubits):
                if mat[r, j+num_qubits] == 1:
                    pivot_col = j
                    pivot_type = 'Z'
                    break
                    
        if pivot_col == -1:
            print(f"Error: Row {r} is 0?")
            continue
            
        # Move pivot to r
        op_swap(r, pivot_col)
        
        # Ensure it is X
        if pivot_type == 'Z':
            op_h(r)
        elif mat[r, r] == 1 and mat[r, r+num_qubits] == 1: # Y
            # Apply S_dag(r) to map Y->X?
            # S: X->Y.
            # S_dag: Y->X.
            # Update rule for S_dag: X_q += Z_q?
            # S: Z+=X.
            # S_dag: Z-=X = Z+X. (Same update rule for Pauli tableau?).
            # Let's check.
            # S_dag: X->Y->-Y? No.
            # S_dag = S^3.
            # S(Z+X) = Z + (Z+X) = X.
            # Yes, Z+=X is the update for both S and S_dag (mod 2).
            # So applying S or S_dag both map Y (1,1) -> X (1,0)?
            # Input (1,1). Z+=X -> Z=1+1=0. Output (1,0).
            # Yes!
            op_s(r) 
            # Now we have X.
            
        # Now we have X at (r, r).
        # We want to clear X from other columns in this row (j > r).
        # Using CNOTs?
        # To clear X_j using X_r:
        # We need X_j += X_r.
        # CNOT(c, t): X_t += X_c.
        # c=r, t=j.
        for j in range(r+1, num_qubits):
            if mat[r, j] == 1:
                op_cnot(r, j)
                
        # Now we have X only at r (in X-block).
        # What about Z-block?
        # We might have Zs.
        # If we have Z_r, it commutes with X_r?
        # No, X_r Z_r = -iY_r.
        # But this is a stabilizer.
        # Generators must commute.
        # Self-commutator is always 0.
        # So we can have Y?
        # But we forced it to be X earlier.
        # If we had Y, we applied S to make it X.
        # So Z-component at r must be 0.
        
        # What about Zs at j > r?
        # We can clear them?
        # To clear Z_j using X_r? No.
        # To clear Z_j using ...?
        # We want to make the stabilizer X_r.
        # So we want to remove Z_j.
        # If we have Z_j, we can apply CZ(r, j)?
        # CZ(c, t): X_c -> X_c Z_t, X_t -> X_t Z_c. Zs unchanged.
        # If we have X_r Z_j.
        # Apply CZ(r, j).
        # X_r -> X_r Z_j.
        # So X_r Z_j -> (X_r Z_j) Z_j = X_r.
        # YES!
        # CZ(r, j) removes Z_j from X_r term.
        
        for j in range(r+1, num_qubits):
            if mat[r, j+num_qubits] == 1:
                # Apply CZ(r, j)
                # CZ is symmetric.
                # Update: X_r += Z_j? No.
                # Update rule for CZ(c, t):
                # Z_c += X_t
                # Z_t += X_c
                # X unchanged? No.
                # X_c -> X_c Z_t.
                # X_t -> X_t Z_c.
                # In tableau (X, Z columns):
                # Z_c += X_t.
                # Z_t += X_c.
                # We want to eliminate Z_j in row r.
                # Generator is X_r Z_j.
                # We want X_r.
                # We apply CZ(r, j).
                # Generator transforms:
                # X_r -> X_r Z_j.
                # Z_j -> Z_j.
                # So X_r Z_j -> X_r Z_j Z_j = X_r.
                # Correct.
                # In tableau:
                # Z_r += X_j? No.
                # Z_j += X_r.
                # X_r has 1. So Z_j += 1.
                # If Z_j was 1, now 0.
                # Correct.
                
                # Check Stim's CZ definition? Standard CZ.
                # ops.append(("CZ", [r, j]))
                # Manually update mat.
                mat[:, r+num_qubits] ^= mat[:, j]
                mat[:, j+num_qubits] ^= mat[:, r]
                ops.append(("CZ", [r, j]))

    # After this loop, for r < 34, row r should be exactly X_r.
    # What about columns 34, 35?
    # We simplified X and Z for j > r.
    # This includes 34, 35.
    # So row r is X_r.
    # Generators are X_0, X_1, ..., X_33.
    # This stabilizes |+> on 0..33.
    # And 34, 35 are free.
    # We can prepare them in |+> too (stabilized by X_34, X_35).
    # Or |0> (stabilized by Z_34, Z_35).
    # Since we want a valid circuit, we can prepare |0> or |+>.
    # The prompt doesn't specify state on 34, 35, only that it satisfies the 34 generators.
    # But usually "prepare stabilizer state" implies a pure state on N qubits.
    # So we should prepare a pure state.
    # Let's pick |+> on 34, 35.
    
    # So the target state is |+>^{otimes 36}.
    # The circuit is:
    # 1. Prepare |+> on all 36 qubits.
    # 2. Apply inverse of ops.
    
    c = stim.Circuit()
    for i in range(num_qubits):
        c.append("H", [i])
        
    for gate, args in reversed(ops):
        c.append(gate, args)
        
    # Write to file
    with open("circuit.stim", "w") as f:
        f.write(str(c))
        
    print("Circuit generated.")

if __name__ == "__main__":
    solve()
