import stim
import networkx as nx

def analyze_conflicts():
    with open("stabilizers_148.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    stabilizers = [stim.PauliString(line) for line in lines]
    n = len(stabilizers)
    
    conflicts = []
    for i in range(n):
        for j in range(i + 1, n):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                conflicts.append((i, j))
    
    print(f"Total stabilizers: {n}")
    print(f"Number of anticommuting pairs: {len(conflicts)}")
    
    if len(conflicts) > 0:
        print("Anticommuting pairs (indices):")
        for c in conflicts[:10]:
            print(c)
        if len(conflicts) > 10:
            print("...")
            
    # Build conflict graph
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(conflicts)
    
    # Simple greedy removal
    # We want to keep as many as possible. This is Maximum Independent Set.
    # We can try to remove the node with highest degree recursively.
    
    keep_indices = []
    
    # Heuristic: verify if it's bipartite or simple
    print(f"Graph stats: Nodes={G.number_of_nodes()}, Edges={G.number_of_edges()}")
    
    # Heuristic algorithm for MIS
    # Sort nodes by degree (ascending? No, we want to keep low degree nodes? 
    # Actually we want to remove high degree nodes to break conflicts.)
    # Let's just use networkx maximal_independent_set (which is not maximum, but approximation)
    # or maximum_independent_set if available (might be slow for large graphs, but 146 nodes is small).
    
    # Try exact MIS if graph is small enough
    try:
        mis = nx.algorithms.mis.maximum_independent_set(G)
        print(f"Found Maximum Independent Set of size: {len(mis)}")
        keep_indices = sorted(list(mis))
    except Exception as e:
        print(f"Exact MIS failed: {e}. Using greedy.")
        mis = nx.algorithms.mis.maximal_independent_set(G)
        print(f"Found Maximal Independent Set of size: {len(mis)}")
        keep_indices = sorted(list(mis))

    # Save the kept stabilizers to a new file
    kept_lines = [lines[i] for i in keep_indices]
    with open("stabilizers_kept.txt", "w") as f:
        f.write("\n".join(kept_lines))
        
    print(f"Saved {len(kept_lines)} commuting stabilizers to stabilizers_kept.txt")

if __name__ == "__main__":
    analyze_conflicts()
