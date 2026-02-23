import stim
import sys
import networkx as nx

def solve_mis():
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186_clean.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Total stabilizers: {len(stabilizers)}")
    
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    # Check commutativity
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                
    print(f"Anticommuting pairs count: {len(anticommuting_pairs)}")

    # Keep track of which ones to remove
    to_remove = set()
    
    # Simple greedy removal
    # Count conflicts per stabilizer
    conflict_counts = {i: 0 for i in range(len(paulis))}
    for i, j in anticommuting_pairs:
        conflict_counts[i] += 1
        conflict_counts[j] += 1
        
    # Iteratively remove max conflict one
    while True:
        # Re-count conflicts considering removed ones
        current_conflicts = {i: 0 for i in range(len(paulis)) if i not in to_remove}
        has_conflict = False
        for i, j in anticommuting_pairs:
            if i not in to_remove and j not in to_remove:
                current_conflicts[i] += 1
                current_conflicts[j] += 1
                has_conflict = True
        
        if not has_conflict:
            break
            
        # Find max
        max_conflict_idx = max(current_conflicts, key=current_conflicts.get)
        to_remove.add(max_conflict_idx)
        print(f"Removing stabilizer {max_conflict_idx} (conflicts: {current_conflicts[max_conflict_idx]})")
        
    print(f"Removed {len(to_remove)} stabilizers.")
    
    subset_indices = sorted([i for i in range(len(paulis)) if i not in to_remove])
    subset_stabilizers = [paulis[i] for i in subset_indices]
    
    try:
        # Use BOTH flags
        tableau = stim.Tableau.from_stabilizers(subset_stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit()
        print("Successfully generated circuit for subset.")
        
        with open(r'data/gemini-3-pro-preview/agent_files/circuit_186_subset.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve_mis()
