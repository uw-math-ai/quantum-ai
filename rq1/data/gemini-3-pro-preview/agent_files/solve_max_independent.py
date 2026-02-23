import stim
import networkx as nx

with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

# Pad
for i in range(len(stabs)):
    if len(stabs[i]) < 180:
        stabs[i] = stabs[i] + 'I' * (180 - len(stabs[i]))

paulis = [stim.PauliString(s) for s in stabs]
n = len(paulis)

G = nx.Graph()
G.add_nodes_from(range(n))

print("Building conflict graph...")
for i in range(n):
    for j in range(i+1, n):
        if not paulis[i].commutes(paulis[j]):
            G.add_edge(i, j)

print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Find vertex cover? No, maximum independent set.
# We want to keep the maximum number of vertices such that no two are connected.
# This is the Maximum Independent Set problem.
# NetworkX has a solver.

print("Solving Maximum Independent Set...")
# approximate? Or exact if small?
# The graph size is 164. Exact might be slow if dense.
# Let's try heuristic first.
mis = nx.algorithms.mis.maximal_independent_set(G)
# But maximal is not maximum.
# Let's try to remove minimum vertex cover.
# Complement graph -> Max Clique.

# Or just use a simple heuristic: remove node with highest degree until no edges.
removed = []
H = G.copy()
while H.number_of_edges() > 0:
    # find max degree node
    degrees = dict(H.degree())
    max_node = max(degrees, key=degrees.get)
    removed.append(max_node)
    H.remove_node(max_node)

print(f"Heuristic removed {len(removed)} nodes: {removed}")
print(f"Remaining nodes: {n - len(removed)}")

# Try exact on the small components if possible?
# But removing high degree nodes is probably best.

# Let's verify the "removed" set resolves all conflicts.
# The remaining nodes in H are independent.

kept_indices = sorted(list(H.nodes()))
print(f"Kept indices: {kept_indices}")

# Generate circuit with kept indices
kept_paulis_final = [paulis[i] for i in kept_indices]

try:
    tableau = stim.Tableau.from_stabilizers(kept_paulis_final, allow_underconstrained=True, allow_redundant=True)
    circuit = tableau.to_circuit("elimination")
    
    # Save circuit
    with open(r'data/gemini-3-pro-preview/agent_files/circuit_optimized.stim', 'w') as f:
        f.write(str(circuit))
        
    print("Circuit generated and saved.")
    
except Exception as e:
    print(f"Error generating circuit: {e}")
