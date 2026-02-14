import stim
import sys

def solve():
    with open("block_stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    n = len(stabs[0])
    num_stabs = len(stabs)
    
    # Represent as binary matrix
    # xs[i, j] = 1 if stabilizer i has X or Y on qubit j
    # zs[i, j] = 1 if stabilizer i has Z or Y on qubit j
    xs = []
    zs = []
    for s in stabs:
        x_row = [1 if c in 'XY' else 0 for c in s]
        z_row = [1 if c in 'ZY' else 0 for c in s]
        xs.append(x_row)
        zs.append(z_row)
        
    # We will record the gates we apply.
    # We apply gates to the right of the state, which corresponds to conjugating stabilizers.
    # $S' = U S U^\dagger$.
    # We want to reach state where stabilizers are Z_0, Z_1, ..., Z_{n-1}.
    # The circuit to prepare the state is the INVERSE of the gates we applied.
    
    gates = []
    
    # Helper to apply gate
    def apply_H(q):
        gates.append(("H", q))
        for i in range(num_stabs):
            xs[i][q], zs[i][q] = zs[i][q], xs[i][q]
            
    def apply_S(q):
        # S: X->Y, Z->Z. Y=XZ.
        # So new X = old X (since Y has X part). Wait.
        # X = [1,0], Z = [0,1], Y = [1,1]
        # S(X) = Y = [1,1].
        # S(Z) = Z = [0,1].
        # S(Y) = -X = [1,0] (ignoring phase for now).
        # In terms of bits:
        # x_new = x_old ^ z_old (if z_old=1, it flips X?)
        # Wait.
        # X(1,0) -> Y(1,1). Z(0,1) -> Z(0,1).
        # So z_new = z_old. x_new = x_old? No.
        # If input is X (1,0): output Y (1,1). x becomes 1, z becomes 1.
        # If input is Z (0,1): output Z (0,1). x becomes 0, z becomes 1.
        # If input is Y (1,1): output X (1,0). x becomes 1, z becomes 0.
        # So:
        # z_new = z_old ^ x_old
        # x_new = x_old? No.
        # (1,0) -> (1,1): z becomes 1 (0^1). x stays 1.
        # (0,1) -> (0,1): z becomes 1 (1^0). x stays 0.
        # (1,1) -> (1,0): z becomes 0 (1^1). x stays 1.
        # So: z_new = z_old ^ x_old. x_new = x_old.
        gates.append(("S", q))
        for i in range(num_stabs):
            zs[i][q] = zs[i][q] ^ xs[i][q]
            
    def apply_CX(c, t):
        # CX(c, t):
        # X_c -> X_c X_t
        # Z_t -> Z_c Z_t
        # X_t -> X_t
        # Z_c -> Z_c
        gates.append(("CX", c, t))
        for i in range(num_stabs):
            xs[i][t] = xs[i][t] ^ xs[i][c] # X propagates from control to target
            zs[i][c] = zs[i][c] ^ zs[i][t] # Z propagates from target to control
            
    # Row operations (multiply stabilizers)
    def row_mult(dst, src):
        # S_dst = S_dst * S_src
        for j in range(n):
            xs[dst][j] = xs[dst][j] ^ xs[src][j]
            zs[dst][j] = zs[dst][j] ^ zs[src][j]
            
    # Gaussian elimination to form Z_0, ..., Z_{n-1}
    # Step 1: Make X matrix identity-like (diagonal 1s)
    
    # We iterate over columns j = 0 to n-1
    # We want to place an X on diagonal (j,j) and clear other X's in column j.
    # And clear Z's in column j?
    
    for j in range(n):
        # Find pivot in rows k >= j with X on column j
        pivot = -1
        for k in range(j, num_stabs):
            if xs[k][j]:
                pivot = k
                break
                
        if pivot == -1:
            # No X on column j. Try to find Z.
            for k in range(j, num_stabs):
                if zs[k][j]:
                    pivot = k
                    break
            
            if pivot != -1:
                # Found Z. Apply H to swap Z->X.
                apply_H(j)
                # Now xs[pivot][j] should be 1.
            else:
                # Column j is empty in rows >= j.
                # This implies dependency or unused qubit.
                # Since we have 19 stabs for 19 qubits, this shouldn't happen if full rank.
                print(f"Error: Rank deficiency at column {j}")
                continue
                
        # Swap row j and pivot
        if pivot != j:
            xs[j], xs[pivot] = xs[pivot], xs[j]
            zs[j], zs[pivot] = zs[pivot], zs[j]
            
        # Now xs[j][j] = 1.
        # Eliminate X on column j for all other rows k != j
        for k in range(num_stabs):
            if k != j and xs[k][j]:
                row_mult(k, j)
                
        # Now column j has X only at row j.
        # Eliminate Z on column j for all rows?
        # If we have X_j on row j, and Z_j on row k.
        # They anticommute at qubit j.
        # But stabilizers must commute.
        # So if row k has Z_j, it must anticommute with row j somewhere else?
        # Or row j also has Z_j (i.e. Y_j)?
        
        # Actually, standard form is:
        # X part is Identity.
        # Z part is arbitrary?
        # No, we want to reduce to single Z's eventually.
        
        # Let's perform the "standard form" reduction first (X part -> I).
        # We did that for column j.
        # Now proceed to next column.
        
    # Now X matrix is (roughly) Identity.
    # xs[j][j] = 1. xs[k][j] = 0 for k != j.
    # So row j is X_j * Z_part.
    # We want to eliminate the Z parts to get X_j (or Z_j via H).
    # Wait, if we have X_j Z_something, we can apply Phase gate?
    # If we have Y_j (X_j Z_j), applying S gives X_j? No.
    # S(X) = Y. S(Y) = -X. S(Z) = Z.
    # S^dagger(Y) = X.
    # So if we have Y_j, apply S^dagger (or S S S) to get X_j.
    # Ideally we want Z_j.
    # So if we have X_j, apply H to get Z_j.
    
    # But we have off-diagonal Z's too.
    # Row j: X_j * Product(Z_k).
    # We can eliminate Z_k (for k > j) using CNOTs?
    # If we apply CNOT(j, k), X_j -> X_j X_k. That creates X_k on row j. Bad.
    # If we apply CNOT(k, j), Z_j -> Z_k Z_j. That changes Z.
    
    # Correct approach for second pass (clearing Z's):
    # We have stabilizers $g_i \approx X_i \dots$
    # We want to clear Z components.
    # First, for each $i$, remove $Z_i$ from $g_i$ (make it $X_i$).
    # If $g_i$ has $Z_i$ (so it is $Y_i \dots$), apply $S_i$ (or $S^\dagger$) to make it $X_i \dots$.
    # S maps X->Y, Y->-X.
    # If we have Y, applying S gives -X (good).
    # So if $xs[i][i] == 1$ and $zs[i][i] == 1$: apply S(i).
    
    for i in range(n):
        if xs[i][i] and zs[i][i]:
            apply_S(i)
            # Now xs[i][i]=1, zs[i][i]=0 (X).
            
    # Now diagonal is pure X.
    # Now remove off-diagonal Z's.
    # We have $g_i = X_i \otimes Z_{something}$.
    # If $g_i$ has $Z_k$ (k != i), we can remove it by applying CNOT?
    # We want to transform $X_i Z_k \to X_i$.
    # CNOT(i, k): $X_i \to X_i X_k$, $Z_k \to Z_k$.
    # $X_i Z_k \to X_i X_k Z_k = X_i Y_k$.
    # Not quite.
    
    # Actually, we can assume the target state is a graph state (up to local Cliffords).
    # The generators are $X_i \prod Z_k$.
    # This corresponds to graph state generators $K_i = X_i \prod_{j \in N(i)} Z_j$.
    # So if we have exactly this form, we are in a graph state basis.
    # To prepare a graph state from $|+\rangle^{\otimes n}$:
    # Apply CZ(i, j) for every edge $(i, j)$.
    # To prepare from $|0\rangle^{\otimes n}$:
    # Apply H to all, then CZs.
    
    # So if we have $g_i = X_i \prod_{k \ne i} Z_k^{A_{ik}}$,
    # We just need to apply $H^{\otimes n}$ to map $Z_i \to X_i$.
    # Then the stabilizers become $Z_i \prod X_k$.
    # Wait, standard graph state is stabilized by $X_i \prod Z_k$.
    # The state is $|G\rangle$.
    # We want to map $|0\rangle \to |G\rangle$.
    # Circuit: H on all. CZ on edges.
    
    # So if our current stabilizers are $g_i = X_i \prod Z_k^{A_{ik}}$,
    # Then we are done! The circuit (inverse of what we did) is:
    # (Operations to diagonalize X) then (Correction to match graph form).
    # But we want to reach $Z_i$.
    # If we have $g_i = X_i \prod Z_k$, applying H on all gives $Z_i \prod X_k$.
    # That's not single Z.
    
    # Let's go backwards.
    # We want $g_i = Z_i$.
    # Currently $g_i = X_i \prod Z_k$.
    # If we apply $CZ(i, k)$, $X_i \to X_i Z_k$.
    # So $X_i Z_k \to X_i Z_k Z_k = X_i$.
    # So applying CZ gates can strip the Z terms!
    # Yes! CZ(i, k) transforms $X_i \to X_i Z_k$ and $X_k \to X_k Z_i$.
    # It removes $Z_k$ from row i (if present) AND removes $Z_i$ from row k (if present).
    # Since stabilizers commute, the adjacency matrix must be symmetric.
    # $A_{ik} = 1$ iff $Z_k$ in row i.
    # And $Z_i$ in row k.
    # So we can just clear the Z's using CZs.
    
    # Algorithm to clear Z off-diagonals:
    for i in range(n):
        for k in range(i+1, n):
            if zs[i][k]:
                # There is a Z_k in row i.
                # This implies there should be a Z_i in row k (by commutation).
                # Apply CZ(i, k).
                # X_i -> X_i Z_k.
                # X_k -> X_k Z_i.
                apply_CX(i, k) # Wait, CZ is symmetric. Stim uses CZ.
                # Actually my `apply_CX` was CNOT.
                # I need `apply_CZ`.
                
    # But wait, I don't have apply_CZ helper. Let's add it.
    pass

    # After clearing Z's, we have $g_i = X_i$.
    # Finally apply H on all to get $g_i = Z_i$.
    
    # Then the state is $|0\rangle$.
    # The preparation circuit is the inverse of the sequence.
    
    return gates

# ... I will modify the script to include apply_CZ and run it.
