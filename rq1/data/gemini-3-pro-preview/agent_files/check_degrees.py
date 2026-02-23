import stim
import networkx as nx

with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]
for i in range(len(stabs)):
    if len(stabs[i]) < 180: stabs[i] += 'I'*(180-len(stabs[i]))

paulis = [stim.PauliString(s) for s in stabs]
G = nx.Graph()
G.add_nodes_from(range(len(paulis)))
for i in range(len(paulis)):
    for j in range(i+1, len(paulis)):
        if not paulis[i].commutes(paulis[j]):
            G.add_edge(i, j)

degrees = dict(G.degree())
sorted_deg = sorted(degrees.items(), key=lambda item: item[1], reverse=True)
print("Top 10 highest degree nodes:")
for node, deg in sorted_deg[:10]:
    if deg > 0:
        print(f"Node {node}: degree {deg}")

# Try removing top node and see
removed = []
H = G.copy()
while H.number_of_edges() > 0:
    deg = dict(H.degree())
    max_node = max(deg, key=deg.get)
    removed.append(max_node)
    H.remove_node(max_node)

print(f"Removed: {removed}")
