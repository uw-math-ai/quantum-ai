import stim
import numpy as np
from typing import List

def solve():
    # Load stabilizers
    with open('stabilizers_161_fixed.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Convert to stim.PauliString
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    # Identify anticommuting pairs
    n = len(paulis)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                
    print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
    
    # Heuristic: Find a large commuting subset
    # Sort by number of conflicts? Or just greedy?
    # Or try to fix them?
    
    # Let's try to remove the minimum number of stabilizers to make the set commuting.
    # We can model this as a Maximum Independent Set problem on the conflict graph.
    # Or simpler: greedy removal of the one with most conflicts.
    
    if anticommuting_pairs:
        print(f"Conflicts found: {anticommuting_pairs}")
        
    keep_indices = set(range(n))
    while True:
        # Recompute conflicts for remaining
        conflict_counts = {i: 0 for i in keep_indices}
        has_conflict = False
        
        # We need to iterate over pairs within keep_indices
        keep_list = sorted(list(keep_indices))
        for i_idx, i in enumerate(keep_list):
            for j in keep_list[i_idx+1:]:
                if not paulis[i].commutes(paulis[j]):
                    conflict_counts[i] += 1
                    conflict_counts[j] += 1
                    has_conflict = True
        
        if not has_conflict:
            break
            
        # Remove the one with max conflicts
        remove_idx = max(conflict_counts, key=conflict_counts.get)
        print(f"Removing stabilizer index {remove_idx} with {conflict_counts[remove_idx]} conflicts.")
        print(f"Removed stabilizer: {paulis[remove_idx]}")
        keep_indices.remove(remove_idx)
        
    print(f"Kept {len(keep_indices)} stabilizers.")
    kept_paulis = [paulis[i] for i in sorted(list(keep_indices))]
    
    # Try to generate circuit for the subset
    try:
        tableau = stim.Tableau.from_stabilizers(kept_paulis, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        
        # We need to verify against ALL original stabilizers.
        # But we know some will fail (the removed ones).
        # We should submit this circuit and see what happens.
        # Maybe we can fix the others later?
        
        print("Generated circuit for subset.")
        return circuit
        
    except Exception as e:
        print(f"Error generating circuit: {e}")
        return None

if __name__ == "__main__":
    circuit = solve()
    if circuit:
        with open('circuit_161_subset.stim', 'w') as f:
            f.write(str(circuit))
