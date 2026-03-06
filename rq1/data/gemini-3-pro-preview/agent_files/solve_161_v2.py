
import stim
import collections

def solve():
    # Read from the file I created with the prompt's stabilizers
    input_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_161.txt'
    output_file = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_161_v2.stim'
    
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    all_stabilizers = [stim.PauliString(line) for line in lines]
    print(f"Loaded {len(all_stabilizers)} stabilizers.")

    # Greedy removal logic
    active_indices = set(range(len(all_stabilizers)))
    
    while True:
        conflicts = collections.defaultdict(int)
        conflict_pairs = []
        
        current_list = sorted(list(active_indices))
        
        # Check all pairs in current_list
        # O(N^2)
        for i_idx in range(len(current_list)):
            i = current_list[i_idx]
            s_i = all_stabilizers[i]
            for j_idx in range(i_idx + 1, len(current_list)):
                j = current_list[j_idx]
                s_j = all_stabilizers[j]
                
                if not s_i.commutes(s_j):
                    conflicts[i] += 1
                    conflicts[j] += 1
                    conflict_pairs.append((i, j))
        
        if not conflict_pairs:
            break
            
        # Find max conflict
        max_conflict_idx = -1
        max_c = -1
        
        for idx, c in conflicts.items():
            if c > max_c:
                max_c = c
                max_conflict_idx = idx
            elif c == max_c:
                # Tie-break: remove higher index? Or lower?
                # Maybe remove the one that overlaps less with others?
                # For now, just remove higher index to be deterministic.
                if idx > max_conflict_idx:
                    max_conflict_idx = idx
        
        print(f"Removing stabilizer {max_conflict_idx} (conflicts: {max_c})")
        active_indices.remove(max_conflict_idx)
        
    print(f"Remaining stabilizers: {len(active_indices)}")
    
    final_stabilizers = [all_stabilizers[i] for i in sorted(list(active_indices))]

    try:
        tableau = stim.Tableau.from_stabilizers(final_stabilizers, allow_underconstrained=True, allow_redundant=True)
        print("Tableau created successfully with FILTERED stabilizers.")
        circuit = tableau.to_circuit("elimination")
        
        with open(output_file, 'w') as f:
            f.write(str(circuit))
        print(f"Circuit saved to {output_file}")
        
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
