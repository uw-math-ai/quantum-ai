import stim

def check():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\my_stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabs = [stim.PauliString(s) for s in lines]
    
    bad_pairs = []
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                bad_pairs.append((i, j))
                print(f"Anticommute: {i} and {j}")
                # print(f"  {stabs[i]}")
                # print(f"  {stabs[j]}")

    print(f"Found {len(bad_pairs)} anticommuting pairs.")
    
    # Check if we can just drop a few
    # We want to find a maximal consistent subset.
    # This is equivalent to finding a maximum clique in the commutation graph.
    # Or maximum independent set in the anticommutation graph.
    
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(len(stabs)))
    G.add_edges_from(bad_pairs)
    
    # We want to remove minimum number of nodes to make graph edgeless.
    # This is Minimum Vertex Cover.
    # The complement is Maximum Independent Set.
    
    # NetworkX has approximations or exact solvers for small graphs.
    # Since N=98, maybe exact is too slow but let's try approximation.
    
    # Actually, verify if just dropping 119 fixed it in previous memories?
    # Here let's see which ones are problematic.
    
    min_cover = nx.algorithms.approximation.min_weighted_vertex_cover(G)
    print(f"Approximate minimum vertex cover size: {len(min_cover)}")
    print(f"Nodes to remove: {sorted(list(min_cover))}")

if __name__ == "__main__":
    check()
