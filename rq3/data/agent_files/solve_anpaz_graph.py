import stim
import numpy as np
import random

def solve():
    print("Loading stabilizers...")
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\current_task_stabilizers.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Load baseline for comparison
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\current_baseline.stim', 'r') as f:
        baseline = stim.Circuit(f.read())
    baseline_cx = 0
    for op in baseline:
        if op.name == "CX":
            baseline_cx += len(op.targets_copy()) // 2
    print(f"Baseline CX count: {baseline_cx}")

    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_redundant=True, allow_underconstrained=True)
    n = len(tableau)
    print(f"Number of qubits: {n}")
    
    xs = np.zeros((n, n), dtype=int)
    zs = np.zeros((n, n), dtype=int)
    
    for i in range(n):
        ps = tableau.z_output(i)
        for k in range(n):
            val = ps[k] # 0=I, 1=X, 2=Y, 3=Z
            if val == 1 or val == 2: xs[i, k] = 1
            if val == 2 or val == 3: zs[i, k] = 1
            
    local_cliffords = [[] for _ in range(n)] 
    
    # Gaussian elimination to form graph state
    for i in range(n):
        # 1. Try to get X_ii = 1
        pivot_row = -1
        for r in range(i, n):
            if xs[r, i] == 1:
                pivot_row = r
                break
        
        if pivot_row == -1:
            for r in range(i, n):
                if zs[r, i] == 1:
                    pivot_row = r
                    break
            
            if pivot_row != -1:
                xs[:, i], zs[:, i] = zs[:, i].copy(), xs[:, i].copy()
                local_cliffords[i].append("H")
            else:
                pass
        
        if pivot_row != -1:
            if pivot_row != i:
                xs[[i, pivot_row]] = xs[[pivot_row, i]]
                zs[[i, pivot_row]] = zs[[pivot_row, i]]
            
            for r in range(n):
                if r != i and xs[r, i] == 1:
                    xs[r] ^= xs[i]
                    zs[r] ^= zs[i]
            
            if zs[i, i] == 1:
                zs[:, i] ^= xs[:, i]
                local_cliffords[i].append("S")
    
    adj = zs.copy()
    for i in range(n):
        adj[i, i] = 0
        
    if not np.allclose(adj, adj.T):
        print("Warning: Adjacency matrix not symmetric! Symmetrizing...")
        adj = (adj + adj.T) % 2
        
    print(f"Initial edges: {np.sum(adj)//2}")

    # OPTIMIZATION: Local Complementation
    current_adj = adj.copy()
    current_edges = np.sum(current_adj) // 2
    lc_ops = [] 
    
    nodes = list(range(n))
    best_edges = current_edges
    best_lc_ops = []

    # Try simple greedy
    for _ in range(5): 
        random.shuffle(nodes)
        temp_adj = current_adj.copy()
        temp_lc_ops = []
        temp_edges = current_edges
        
        improved = True
        while improved:
            improved = False
            for v in nodes:
                neighbors = np.where(temp_adj[v])[0]
                if len(neighbors) < 2: continue
                
                subgraph_edges = 0
                possible_edges = len(neighbors) * (len(neighbors)-1) // 2
                
                for i in range(len(neighbors)):
                    for j in range(i+1, len(neighbors)):
                        if temp_adj[neighbors[i], neighbors[j]]:
                            subgraph_edges += 1
                            
                delta = possible_edges - 2 * subgraph_edges
                
                if delta < 0:
                    for i in range(len(neighbors)):
                        u = neighbors[i]
                        for j in range(i+1, len(neighbors)):
                            w = neighbors[j]
                            temp_adj[u, w] ^= 1
                            temp_adj[w, u] ^= 1
                    
                    temp_lc_ops.append(v)
                    temp_edges += delta
                    improved = True
        
        if temp_edges < best_edges:
            best_edges = temp_edges
            best_lc_ops = list(temp_lc_ops)
            print(f"New best edges: {best_edges}")
            
    print(f"Optimized Edges: {best_edges}")
    
    # Reconstruct final adjacency
    final_adj = adj.copy()
    for v in best_lc_ops:
        neighbors = np.where(final_adj[v])[0]
        for i in range(len(neighbors)):
            u = neighbors[i]
            for j in range(i+1, len(neighbors)):
                w = neighbors[j]
                final_adj[u, w] ^= 1
                final_adj[w, u] ^= 1

    circ_opt = stim.Circuit()
    circ_opt.append("H", range(n))
    
    rows, cols = np.where(np.triu(final_adj, 1))
    for r, c in zip(rows, cols):
        circ_opt.append("CZ", [r, c]) # CZ is CX + H's
    
    # Correction circuit
    correction_circ = stim.Circuit()
    
    # Replay LCs to build U_LC^dag
    # We must replay them on the graph to know neighbors at each step
    replay_adj = adj.copy()
    
    # We apply U_v1^d then U_v2^d ... ? No.
    # |G_final> = U_k ... U_1 |G_initial>
    # |psi> = L^d |G_initial> = L^d U_1^d ... U_k^d |G_final>
    # So append U_k^d, then U_{k-1}^d ... then U_1^d
    
    for v in reversed(best_lc_ops):
        # We need neighbors of v at the moment AFTER v was applied? 
        # No, U_v depends on N(v) BEFORE operation.
        # But we are applying inverses in reverse.
        # So we need N(v) at step k (before U_k was applied).
        # We can just compute the sequence forward and store the operations.
        pass
    
    # Forward pass to generate inverse operations
    ops_list = []
    temp_adj_fwd = adj.copy()
    for v in best_lc_ops:
        neighbors = np.where(temp_adj_fwd[v])[0]
        # U_v^dag = (prod S_u) SQRT_X_DAG_v
        ops_list.append((v, list(neighbors)))
        
        # Update graph
        for i in range(len(neighbors)):
            u = neighbors[i]
            for j in range(i+1, len(neighbors)):
                w = neighbors[j]
                temp_adj_fwd[u, w] ^= 1
                temp_adj_fwd[w, u] ^= 1

    # Now append inverses in reverse order
    for v, neighbors in reversed(ops_list):
        correction_circ.append("SQRT_X_DAG", [v])
        for u in neighbors:
            correction_circ.append("S", [u])

    # Initial local corrections
    for i in range(n):
        ops = local_cliffords[i]
        for op in reversed(ops):
            if op == "H":
                correction_circ.append("H", [i])
            elif op == "S":
                correction_circ.append("S_DAG", [i])
                
    full_circ = circ_opt + correction_circ
    
    # Decompose CZ to CX for fair comparison/submission
    # CZ t c = H t CX c t H t
    final_circ = stim.Circuit()
    for op in full_circ:
        if op.name == "CZ":
            targets = op.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                final_circ.append("H", [t])
                final_circ.append("CX", [c, t])
                final_circ.append("H", [t])
        else:
            final_circ.append(op)
            
    # Optimize final circuit (merge H's, cancel gates)
    # Stim doesn't have a built-in "optimize" that reduces gates significantly for unitaries.
    # But we can do a simple peephole: H H -> I.
    # Actually, let's just count and see.
    
    final_cx = 0
    for op in final_circ:
        if op.name == "CX":
            final_cx += len(op.targets_copy()) // 2
            
    print(f"Graph State Total CX: {final_cx}")
    
    # Verify
    sim = stim.TableauSimulator()
    sim.do(final_circ)
    valid_opt = True
    for s in stabilizers:
        if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
            valid_opt = False
            break
    print(f"Optimized Valid: {valid_opt}")
    
    if valid_opt:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\candidate_opt.stim', 'w') as f:
            f.write(str(final_circ))

if __name__ == "__main__":
    solve()
