import stim
import collections

def solve():
    with open("stabilizers_161.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    all_stabilizers = [stim.PauliString(line) for line in lines]
    active_indices = set(range(len(all_stabilizers)))
    
    print(f"Total stabilizers: {len(active_indices)}")

    while True:
        conflicts = collections.defaultdict(int)
        conflict_pairs = []
        
        current_list = sorted(list(active_indices))
        for idx_i in range(len(current_list)):
            i = current_list[idx_i]
            s_i = all_stabilizers[i]
            for idx_j in range(idx_i + 1, len(current_list)):
                j = current_list[idx_j]
                s_j = all_stabilizers[j]
                if not s_i.commutes(s_j):
                    conflicts[i] += 1
                    conflicts[j] += 1
                    conflict_pairs.append((i, j))
        
        if not conflict_pairs:
            break
            
        # Greedy removal: remove the one with most conflicts
        # Tie-breaking: remove higher index (arbitrary, or try to keep lower indices?)
        # Let's remove the one with max conflicts.
        # Find the one with max conflicts.
        max_conflict_idx = -1
        max_conflicts = -1
        
        for k, v in conflicts.items():
            if v > max_conflicts:
                max_conflicts = v
                max_conflict_idx = k
            elif v == max_conflicts:
                # Tie-break: prefer keeping lower indices if possible, so remove higher?
                # Or maybe random.
                # Let's remove the larger index if tied.
                if k > max_conflict_idx:
                    max_conflict_idx = k
        
        print(f"Removing stabilizer {max_conflict_idx} which has {conflicts[max_conflict_idx]} conflicts.")
        active_indices.remove(max_conflict_idx)

    print(f"Remaining compatible stabilizers: {len(active_indices)}")
    
    final_stabilizers = [all_stabilizers[i] for i in sorted(list(active_indices))]
    
    try:
        # Use elimination to find a state
        tableau = stim.Tableau.from_stabilizers(final_stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        
        with open("circuit_161.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated and saved to circuit_161.stim")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
