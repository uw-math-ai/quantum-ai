import stim
import networkx as nx

with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

# Pad to 180 length
# The problem statement implies 180 qubits, but generator lengths vary.
# Wait, checking lengths first.
lengths = [len(s) for s in stabs]
max_len = max(lengths)
# print(f"Max length: {max_len}")

# Let's assume 180 based on previous context.
# Or use max_len.
# The user prompt had strings of length 180? (I can check one)
# XZZXIIII...IIII (many I's)
# I'll stick to max_len if it's consistent.

n_qubits = 180
paulis = []
for s in stabs:
    if len(s) < n_qubits:
        s = s + 'I' * (n_qubits - len(s))
    paulis.append(stim.PauliString(s))

n = len(paulis)
G = nx.Graph()
G.add_nodes_from(range(n))

# Build conflict graph
for i in range(n):
    for j in range(i+1, n):
        if not paulis[i].commutes(paulis[j]):
            G.add_edge(i, j)

print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

# Try to find Maximum Independent Set
# 1. Heuristic: remove max degree node
def heuristic_mis(graph):
    H = graph.copy()
    removed = []
    while H.number_of_edges() > 0:
        degrees = dict(H.degree())
        # Break ties randomly? Or deterministic?
        # Deterministic for now
        max_node = max(degrees, key=degrees.get)
        removed.append(max_node)
        H.remove_node(max_node)
    return list(H.nodes())

mis_heuristic = heuristic_mis(G)
print(f"Heuristic MIS size: {len(mis_heuristic)}")

# 2. NetworkX approximation
try:
    mis_approx = nx.algorithms.approximation.maximum_independent_set(G)
    print(f"Approx MIS size: {len(mis_approx)}")
except:
    print("Approx MIS failed or not available.")

# 3. Exact method (might be slow)
# Max Independent Set on G is Max Clique on Complement(G).
# But checking Max Clique on Complement might be slow if G is sparse (Complement is dense).
# G is a conflict graph. Usually sparse?
# If G has few edges (conflicts), MIS is large.
# If G has many edges, MIS is small.
# The previous run removed 5-8 nodes, so MIS is ~156-159.
# This means G is very sparse (mostly isolated nodes).
# So Complement(G) is very dense. Max Clique on dense graph is hard.
# But Max Independent Set on sparse graph is easier?

# Actually, if we only need to remove a few nodes, maybe Vertex Cover is better?
# Size(MIS) + Size(Min Vertex Cover) = |V|.
# We want Max MIS => Min Vertex Cover.
# Vertex Cover on sparse graph?

# Let's try `networkx.algorithms.clique.max_weight_clique` on complement?
# Or `maximum_independent_set` from `clique` module if it exists?
# It doesn't.

# Let's simply try to improve the heuristic by randomizing tie-breaking.
import random
best_mis = mis_heuristic
for _ in range(100):
    H = G.copy()
    current_removed = []
    while H.number_of_edges() > 0:
        degrees = dict(H.degree())
        max_deg = max(degrees.values())
        candidates = [n for n, d in degrees.items() if d == max_deg]
        node_to_remove = random.choice(candidates)
        current_removed.append(node_to_remove)
        H.remove_node(node_to_remove)
    
    current_mis = list(H.nodes())
    if len(current_mis) > len(best_mis):
        best_mis = current_mis
        print(f"Found better MIS size: {len(best_mis)}")

print(f"Best MIS size found: {len(best_mis)}")
kept_indices = sorted(best_mis)

# Save the best circuit
kept_paulis = [paulis[i] for i in kept_indices]
tableau = stim.Tableau.from_stabilizers(kept_paulis, allow_underconstrained=True, allow_redundant=True)
circuit = tableau.to_circuit("elimination")

with open(r'data/gemini-3-pro-preview/agent_files/circuit_improved.stim', 'w') as f:
    f.write(str(circuit))
print("Improved circuit saved to data/gemini-3-pro-preview/agent_files/circuit_improved.stim")
