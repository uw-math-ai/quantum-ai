import stim

def check_comm():
    with open("stabilizers_148.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    stabs = [stim.PauliString(s) for s in lines]
    
    # Check pairwise commutativity
    anticommuting_pairs = []
    conflict_counts = {}
    
    for i in range(len(stabs)):
        for j in range(i + 1, len(stabs)):
            if not stabs[i].commutes(stabs[j]):
                anticommuting_pairs.append((i, j))
                conflict_counts[i] = conflict_counts.get(i, 0) + 1
                conflict_counts[j] = conflict_counts.get(j, 0) + 1

    print(f"Total anticommuting pairs: {len(anticommuting_pairs)}")
    
    if anticommuting_pairs:
        # Simple greedy removal
        # Find the one with most conflicts
        removed = []
        while True:
            # Recompute conflicts for remaining stabs
            current_conflicts = {}
            remaining_indices = [k for k in range(len(stabs)) if k not in removed]
            
            has_conflict = False
            for idx1 in range(len(remaining_indices)):
                i = remaining_indices[idx1]
                for idx2 in range(idx1 + 1, len(remaining_indices)):
                    j = remaining_indices[idx2]
                    if not stabs[i].commutes(stabs[j]):
                        current_conflicts[i] = current_conflicts.get(i, 0) + 1
                        current_conflicts[j] = current_conflicts.get(j, 0) + 1
                        has_conflict = True
            
            if not has_conflict:
                break
                
            # Remove the one with max conflicts
            to_remove = max(current_conflicts, key=current_conflicts.get)
            removed.append(to_remove)
            print(f"Removing stabilizer {to_remove} (conflicts: {current_conflicts[to_remove]})")
        
        print(f"Removed {len(removed)} stabilizers: {removed}")
        print(f"Remaining: {len(stabs) - len(removed)}")
        
        # Generate circuit for the remaining ones
        remaining_stabs = [stabs[i] for i in range(len(stabs)) if i not in removed]
        t = stim.Tableau.from_stabilizers(remaining_stabs, allow_redundant=True, allow_underconstrained=True)
        c = t.to_circuit("elimination")
        with open("circuit_148_attempt.stim", "w") as f:
            f.write(str(c))
        print("Generated circuit_148_attempt.stim for the commuting subset.")

if __name__ == "__main__":
    check_comm()
