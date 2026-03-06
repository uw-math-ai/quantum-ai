import stim
import sys

def check_commutativity(stabilizers):
    num_qubits = len(stabilizers[0])
    num_stabilizers = len(stabilizers)
    
    # Convert to stim Tableaus or just check manually
    # Manual check is easier for raw strings
    
    commutes = True
    anticommuting_pairs = []
    
    for i in range(num_stabilizers):
        for j in range(i + 1, num_stabilizers):
            s1 = stabilizers[i]
            s2 = stabilizers[j]
            
            # Count number of anti-commuting positions
            anticommutes_count = 0
            for k in range(num_qubits):
                p1 = s1[k]
                p2 = s2[k]
                
                if p1 == 'I' or p2 == 'I':
                    continue
                if p1 != p2:
                    anticommutes_count += 1
            
            if anticommutes_count % 2 == 1:
                commutes = False
                anticommuting_pairs.append((i, j))
                # print(f"Stabilizers {i} and {j} anticommute")

    return commutes, anticommuting_pairs

def solve(stabilizers):
    # This function will try to produce a stim circuit using the graph state approach or Gaussian elimination
    # For now, let's just try to find a consistent subset if they are inconsistent
    
    commutes, pairs = check_commutativity(stabilizers)
    print(f"Commutes: {commutes}")
    print(f"Anticommuting pairs count: {len(pairs)}")
    
    if not commutes:
        print("Stabilizers do not commute. Finding maximum consistent subset...")
        # Simple greedy removal
        removed_indices = set()
        for i, j in pairs:
            if i not in removed_indices and j not in removed_indices:
                # Remove the one with higher index, arbitrarily (or maybe the one involved in more conflicts)
                removed_indices.add(j) # simple strategy
        
        print(f"Removing {len(removed_indices)} stabilizers")
        consistent_stabilizers = [s for k, s in enumerate(stabilizers) if k not in removed_indices]
    else:
        consistent_stabilizers = stabilizers

    # Now try to solve for the consistent set using Stim
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in consistent_stabilizers], allow_underconstrained=True)
    c = t.to_circuit()
    return c

if __name__ == "__main__":
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_171.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    c = solve(stabilizers)
    print("Generated circuit")
    # print(c)
    with open("data/gemini-3-pro-preview/agent_files/circuit_171.stim", "w") as f:
        f.write(str(c))
