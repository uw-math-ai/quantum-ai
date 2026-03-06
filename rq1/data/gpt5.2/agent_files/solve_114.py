import stim
import sys
import os

def solve():
    try:
        file_path = r"data\gemini-3-pro-preview\agent_files\stabilizers_114.txt"
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        stabilizers = []
        for line in lines:
            try:
                stabilizers.append(stim.PauliString(line))
            except Exception as e:
                print(f"Error parsing stabilizer: {line}")
                print(e)
                return

        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Check lengths
        for i, s in enumerate(lines):
            if len(s) != 114:
                print(f"Warning: Stabilizer {i} has length {len(s)}")

        # Print problematic ones
        print(f"Stabilizer 8: {lines[8]}")
        print(f"Stabilizer 92: {lines[92]}")

        
    # Try to find a consistent subset
        print("Finding consistent subset...")
        consistent_indices = []
        consistent_stabilizers = []
        
        for i, stab in enumerate(stabilizers):
            is_consistent = True
            for existing_stab in consistent_stabilizers:
                if not stab.commutes(existing_stab):
                    is_consistent = False
                    break
            
            if is_consistent:
                consistent_indices.append(i)
                consistent_stabilizers.append(stab)
        
        print(f"Kept {len(consistent_stabilizers)} out of {len(stabilizers)} stabilizers.")
        dropped_indices = set(range(len(stabilizers))) - set(consistent_indices)
        print(f"Dropped indices: {sorted(list(dropped_indices))}")

        # Strategy 2: Try dropping the ones that cause MOST conflicts
        print("\nStrategy 2: Heuristic based on conflict count")
        
        # Build conflict graph
        adj = {i: set() for i in range(len(stabilizers))}
        for i in range(len(stabilizers)):
            for j in range(i + 1, len(stabilizers)):
                if not stabilizers[i].commutes(stabilizers[j]):
                    adj[i].add(j)
                    adj[j].add(i)
        
        # Iteratively remove node with max degree
        kept_indices = set(range(len(stabilizers)))
        while True:
            # Check if current set is consistent
            max_degree = -1
            node_to_remove = -1
            
            # Recompute degrees within the kept set
            current_conflicts = 0
            for i in kept_indices:
                degree = 0
                for neighbor in adj[i]:
                    if neighbor in kept_indices:
                        degree += 1
                if degree > 0:
                    current_conflicts += 1
                    if degree > max_degree:
                        max_degree = degree
                        node_to_remove = i
            
            if current_conflicts == 0:
                break
            
            print(f"Removing {node_to_remove} with degree {max_degree}")
            kept_indices.remove(node_to_remove)
            
        print(f"Strategy 2 kept {len(kept_indices)} stabilizers.")
        print(f"Dropped: {sorted(list(set(range(len(stabilizers))) - kept_indices))}")
        
        if len(kept_indices) > len(consistent_indices):
            print("Strategy 2 is better! Using it.")
            final_stabilizers = [stabilizers[i] for i in sorted(list(kept_indices))]
        else:
            print("Strategy 1 is better or equal. Using it.")
            final_stabilizers = consistent_stabilizers

        try:
            tableau = stim.Tableau.from_stabilizers(final_stabilizers, allow_redundant=True, allow_underconstrained=True)
            circuit = tableau.to_circuit()
            print("Successfully created circuit from subset!")
            with open("circuit_114.stim", "w") as f:
                f.write(str(circuit))
        except Exception as e:
            print("Failed to create tableau from subset:")
            print(e)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    solve()
