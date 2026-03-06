import stim
import numpy as np

def analyze():
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186.txt') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    n = len(stabilizers)
    
    print(f"Number of stabilizers: {n}")
    
    # Check commutativity
    comm_matrix = np.zeros((n, n), dtype=int)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if not stabilizers[i].commutes(stabilizers[j]):
                comm_matrix[i, j] = 1
                comm_matrix[j, i] = 1
                anticommuting_pairs.append((i, j))

    print(f"Number of anticommuting pairs: {len(anticommuting_pairs)}")
    conflict_counts = {}
    for i, j in anticommuting_pairs:
        print(f"  {i} vs {j}")
        conflict_counts[i] = conflict_counts.get(i, 0) + 1
        conflict_counts[j] = conflict_counts.get(j, 0) + 1
    
    print("\nMost conflicted stabilizers:")
    for idx, count in sorted(conflict_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"Stabilizer {idx}: {count} conflicts")

            
    # Check for consistency with graph state structure
    # Graph states have X generators and Z generators?
    # No, graph states are usually defined by a graph, with generators K_v = X_v \prod_{u \in N(v)} Z_u.
    
    # Let's count X-only and Z-only stabilizers
    x_only = [s for s in stabilizers if all(p in [0, 1] for p in s)] # 0=I, 1=X, 2=Y, 3=Z
    z_only = [s for s in stabilizers if all(p in [0, 3] for p in s)]
    
    print(f"X-only stabilizers: {len(x_only)}")
    print(f"Z-only stabilizers: {len(z_only)}")
    
    # Check weights
    weights = [sum(1 for p in s if p != 0) for s in stabilizers]
    print(f"Weights: {weights}")

if __name__ == "__main__":
    analyze()
