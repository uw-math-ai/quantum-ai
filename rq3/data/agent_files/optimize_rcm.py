import stim
import collections
import heapq

def count_cx(circuit):
    cx = 0
    for op in circuit:
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP"]:
            cx += len(op.targets_copy()) // 2
    return cx

def get_adjacency_graph(num_qubits, stabilizers):
    adj = collections.defaultdict(set)
    for s in stabilizers:
        # Convert PauliString to indices of non-identity
        # s is stim.PauliString
        # We can iterate
        indices = [i for i in range(len(s)) if s[i]]
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                u, v = indices[i], indices[j]
                adj[u].add(v)
                adj[v].add(u)
    return adj

def bfs_ordering(num_qubits, adj, start_node):
    visited = set()
    queue = collections.deque([start_node])
    visited.add(start_node)
    ordering = []
    
    while queue:
        u = queue.popleft()
        ordering.append(u)
        # Neighbors sorted by degree
        neighbors = sorted(list(adj[u]), key=lambda x: len(adj[x]))
        for v in neighbors:
            if v not in visited:
                visited.add(v)
                queue.append(v)
                
    # Handle disconnected
    for i in range(num_qubits):
        if i not in visited:
            queue.append(i)
            visited.add(i)
            while queue:
                u = queue.popleft()
                ordering.append(u)
                neighbors = sorted(list(adj[u]), key=lambda x: len(adj[x]))
                for v in neighbors:
                    if v not in visited:
                        visited.add(v)
                        queue.append(v)
    return ordering

def solve():
    print("Loading stabilizers...")
    with open("stabilizers.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabs = [stim.PauliString(s) for s in lines]
    num_qubits = len(stabs[0])
    print(f"Num qubits: {num_qubits}")
    
    adj = get_adjacency_graph(num_qubits, stabs)
    
    heuristics = []
    
    # 1. Identity
    heuristics.append(("Identity", list(range(num_qubits))))
    
    # 2. RCM
    # Find min degree node
    min_degree_node = min(range(num_qubits), key=lambda x: len(adj[x]))
    bfs = bfs_ordering(num_qubits, adj, min_degree_node)
    rcm = list(reversed(bfs))
    heuristics.append(("RCM", rcm))
    
    # 3. BFS (Cuthill-McKee)
    heuristics.append(("BFS", bfs))
    
    # 4. Degree Asc
    deg_asc = sorted(range(num_qubits), key=lambda x: len(adj[x]))
    heuristics.append(("Degree Asc", deg_asc))
    
    # 5. Degree Desc
    deg_desc = sorted(range(num_qubits), key=lambda x: len(adj[x]), reverse=True)
    heuristics.append(("Degree Desc", deg_desc))

    # 6. Max Clique / Greedy?
    # Simple Greedy: pick node with max overlap with processed nodes?
    
    best_cx = 999999
    best_c = None
    best_name = ""
    
    for name, perm in heuristics:
        # perm: old -> new
        # Wait, if I use perm as map old->new, I need to verify what bfs returns.
        # bfs returns a LIST of nodes in order.
        # So new index 0 is bfs[0]. new index 1 is bfs[1].
        # So node bfs[i] maps to new index i.
        # So perm_map[bfs[i]] = i.
        
        perm_map = {old: new for new, old in enumerate(perm)}
        
        # Construct new stabilizers
        new_stabs = []
        for s in stabs:
            new_ps = stim.PauliString(num_qubits)
            for k in range(len(s)):
                op = s[k]
                if op:
                    new_ps[perm_map[k]] = op
            new_stabs.append(new_ps)
            
        try:
            t = stim.Tableau.from_stabilizers(new_stabs, allow_underconstrained=True)
            c = t.to_circuit(method="elimination")
            
            # Relabel back
            # Map new -> old
            # new index i maps to old index perm[i].
            inv_map = {new: old for new, old in enumerate(perm)}
            
            final_c = stim.Circuit()
            for op in c:
                targets = []
                for t in op.targets_copy():
                    if t.is_qubit_target:
                        targets.append(inv_map[t.value])
                    else:
                        targets.append(t)
                final_c.append(op.name, targets, op.gate_args_copy())
                
            cx = count_cx(final_c)
            print(f"Heuristic {name}: CX={cx}")
            
            if cx < best_cx:
                best_cx = cx
                best_c = final_c
                best_name = name
                best_c.to_file("candidate_opt.stim")
                
        except Exception as e:
            print(f"Error {name}: {e}")
            
    print(f"Best: {best_name} with CX={best_cx}")

if __name__ == "__main__":
    solve()
