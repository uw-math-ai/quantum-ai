import stim
import sys

def solve():
    with open("block_stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    n = len(stabs[0])
    num_stabs = len(stabs)
    
    xs = []
    zs = []
    for s in stabs:
        x_row = [1 if c in 'XY' else 0 for c in s]
        z_row = [1 if c in 'ZY' else 0 for c in s]
        xs.append(x_row)
        zs.append(z_row)
        
    gates = []
    
    def apply_H(q):
        gates.append(("H", [q]))
        for i in range(num_stabs):
            xs[i][q], zs[i][q] = zs[i][q], xs[i][q]
            
    def apply_S(q):
        gates.append(("S", [q]))
        for i in range(num_stabs):
            zs[i][q] = zs[i][q] ^ xs[i][q]

    def apply_CX(c, t):
        gates.append(("CX", [c, t]))
        for i in range(num_stabs):
            xs[i][t] = xs[i][t] ^ xs[i][c]
            zs[i][c] = zs[i][c] ^ zs[i][t]
            
    def apply_CZ(c, t):
        gates.append(("CZ", [c, t]))
        for i in range(num_stabs):
            # X_c -> X_c Z_t
            # X_t -> X_t Z_c
            # Z_c -> Z_c
            # Z_t -> Z_t
            # Update Z based on X
            zs[i][t] = zs[i][t] ^ xs[i][c]
            zs[i][c] = zs[i][c] ^ xs[i][t]

    def row_mult(dst, src):
        for j in range(n):
            xs[dst][j] = xs[dst][j] ^ xs[src][j]
            zs[dst][j] = zs[dst][j] ^ zs[src][j]
            
    # 1. Gaussian elimination to get X identity
    for j in range(n):
        pivot = -1
        for k in range(j, num_stabs):
            if xs[k][j]:
                pivot = k
                break
        
        if pivot == -1:
            for k in range(j, num_stabs):
                if zs[k][j]:
                    pivot = k
                    break
            if pivot != -1:
                apply_H(j)
            else:
                # If column j is empty, check if we can swap with a later column?
                # Usually we assume qubits are ordered.
                # If the stabilizer group has rank < n, we might have empty columns.
                # Here n=19, stabs=19. Should be full rank.
                print(f"Error: Rank deficiency at column {j}")
                continue
                
        if pivot != j:
            xs[j], xs[pivot] = xs[pivot], xs[j]
            zs[j], zs[pivot] = zs[pivot], zs[j]
            
        # Eliminate X on column j for ALL rows k != j
        for k in range(num_stabs):
            if k != j and xs[k][j]:
                row_mult(k, j)
                
    # 2. Clear diagonal Z's (phase corrections)
    for j in range(n):
        if zs[j][j]:
            apply_S(j) # S maps X->Y (adds Z to X part? No adds Z to Z part? Wait.)
            # If we have X (1,0) and Z (0,1).
            # S(X) = Y (1,1).
            # We want to remove Z.
            # If we have Y (1,1), apply S -> -X (1,0).
            # So if xs=1, zs=1, apply S.
            # In my `apply_S`: zs = zs ^ xs.
            # If zs=1, xs=1 -> zs = 1^1 = 0.
            # Correct.
            
    # 3. Clear off-diagonal Z's (graph state corrections)
    for j in range(n):
        for k in range(j+1, n):
            if zs[j][k]: # There is a Z_k on row j
                apply_CZ(j, k)
                
    # 4. Now we have X_j on row j and nothing else.
    # Apply H to get Z_j.
    for j in range(n):
        apply_H(j)
        
    # The circuit we built transforms Target -> |0>.
    # We want |0> -> Target.
    # Inverse circuit.
    
    inv_gates = []
    for op, qubits in reversed(gates):
        if op == "S":
            inv_gates.append(("S_DAG", qubits))
        else:
            inv_gates.append((op, qubits))
            
    # Construct Stim circuit
    c = stim.Circuit()
    for op, qubits in inv_gates:
        c.append(op, qubits)
        
    print(c)

solve()
