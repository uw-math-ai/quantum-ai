import stim
import sys
import networkx as nx

def solve_mis():
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186_clean.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Total stabilizers: {len(stabilizers)}")
    
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    G = nx.Graph()
    G.add_nodes_from(range(len(paulis)))
    
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                G.add_edge(i, j)
                
    print(f"Conflict graph has {G.number_of_edges()} edges.")
    
    # Heuristic for Maximum Independent Set
    # Iteratively remove node with highest degree
    
    mis = set(G.nodes())
    while G.number_of_edges() > 0:
        # Find node with highest degree in current graph
        degrees = dict(G.degree())
        max_deg_node = max(degrees, key=degrees.get)
        
        # Remove it from graph and from our set
        G.remove_node(max_deg_node)
        mis.remove(max_deg_node)
        
    print(f"Found independent set of size: {len(mis)}")
    
    # Now generate circuit for this subset
    subset_indices = sorted(list(mis))
    subset_stabilizers = [paulis[i] for i in subset_indices]
    
    try:
        tableau = stim.Tableau.from_stabilizers(subset_stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        print("Successfully generated circuit for subset.")
        
        with open(r'data/gemini-3-pro-preview/agent_files/circuit_186_subset.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve_mis()
