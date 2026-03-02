import stim
import networkx as nx

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    return [stim.PauliString(s) for s in lines]

def main():
    stabilizers = read_stabilizers('data/gemini-3-pro-preview/agent_files/stabilizers_184.txt')
    n = len(stabilizers)
    print(f"Total stabilizers: {n}")
    
    stabilizers[32] = stim.PauliString(184)
    for idx in [0, 1, 2, 3, 7, 10, 11, 18]:
        stabilizers[32][idx] = "X"
    print("Fixed stabilizer 32.")
    
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)
    
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if not stabilizers[i].commutes(stabilizers[j]):
                G.add_edge(i, j)
                anticommuting_pairs.append((i, j))
                
    print(f"Number of anticommuting pairs: {len(anticommuting_pairs)}")
    
    # We want to find the largest subset of vertices such that no two vertices are connected.
    # This is the Maximum Independent Set problem.
    # NetworkX has a function for this.
    
    max_independent_set = nx.approximation.maximum_independent_set(G)
    # The approximation might not be exact. For 178 nodes, maybe we can find exact solution?
    # max_independent_set is for node cover, wait.
    # maximum_independent_set returns a set of nodes.
    
    # For exact solution on small graphs:
    # complement graph clique
    # G_complement = nx.complement(G)
    # clique = nx.max_weight_clique(G_complement, weight=None)
    
    # Let's try a greedy approach first or use a library function if available.
    # Or just use `nx.max_weight_independent_set`? No, that requires valid weights.
    # Let's use `nx.maximum_independent_set` (exact) if available, or just heuristic.
    # NetworkX `maximum_independent_set` is not in the main namespace for exact, 
    # but `nx.algorithms.clique.max_weight_clique` on complement is exact.
    
    print("Finding maximum consistent subset...")
    # Finding Maximum Independent Set is equivalent to finding Maximum Clique in the complement graph.
    G_complement = nx.complement(G)
    max_clique, _ = nx.max_weight_clique(G_complement, weight=None)
    
    print(f"Size of maximum consistent subset: {len(max_clique)}")
    
    # Let's check which ones are dropped.
    kept_indices = sorted(list(max_clique))
    dropped_indices = sorted(list(set(range(n)) - set(kept_indices)))
    
    print(f"Dropped indices: {dropped_indices}")
    
    # Let's see if we can identify a pattern in the dropped ones.
    for i in dropped_indices:
        print(f"Dropped {i}: {stabilizers[i]}")
        neighbors = sorted(list(G.neighbors(i)))
        print(f"Anticommutes with: {neighbors}")
        for j in neighbors:
            print(f"  {j}: {stabilizers[j]}")

if __name__ == "__main__":
    main()
