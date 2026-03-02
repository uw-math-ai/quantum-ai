import stim
import sys

def solve():
    print("Reading stabilizers...")
    try:
        with open(r'data\gemini-3-pro-preview\agent_files\stabilizers_148.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Stabilizer file not found!")
        return

    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing stabilizer '{line}': {e}")
            return

    n_qubits = len(stabilizers[0])
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {len(stabilizers)}")

    # Check for commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs:
            print(f"  {i} vs {j}")
        # Identify problematic stabilizers
        conflict_counts = {}
        for i, j in anticommuting_pairs:
            conflict_counts[i] = conflict_counts.get(i, 0) + 1
            conflict_counts[j] = conflict_counts.get(j, 0) + 1
        
        sorted_conflicts = sorted(conflict_counts.items(), key=lambda x: x[1], reverse=True)
        print("Most conflicting stabilizers:")
        for idx, count in sorted_conflicts[:10]:
            print(f"  Stabilizer {idx}: {count} conflicts")

        # Suggest removing the most conflicting ones
        to_remove = set()
        for idx, _ in sorted_conflicts:
            # Check if removing this one resolves remaining conflicts
            still_bad = False
            # This is a greedy heuristic
            if idx not in to_remove:
                 to_remove.add(idx)

        # Let's try removing just the top one first
        best_candidate = sorted_conflicts[0][0]
        print(f"Trying to remove stabilizer {best_candidate}")
        
        filtered_stabilizers = [s for k, s in enumerate(stabilizers) if k != best_candidate]
        
        try:
            tableau = stim.Tableau.from_stabilizers(filtered_stabilizers, allow_redundant=True, allow_underconstrained=True)
            circuit = tableau.to_circuit()
            output_path = r'data\gemini-3-pro-preview\agent_files\circuit_148_fixed.stim'
            with open(output_path, 'w') as f:
                f.write(str(circuit))
            print(f"Circuit with {len(filtered_stabilizers)} stabilizers written to {output_path}")
        except Exception as e:
             print(f"Still failed after removing {best_candidate}: {e}")

    else:
        print("All stabilizers commute.")


    try:
        # allow_underconstrained=True is crucial here
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit("MPP") 
        # "MPP" format might be better for preserving the stabilizer structure, but standard gates are safer.
        # Let's use default decomposition first.
        circuit = tableau.to_circuit()
        
        output_path = r'data\gemini-3-pro-preview\agent_files\circuit_148.stim'
        with open(output_path, 'w') as f:
            f.write(str(circuit))
        print(f"Circuit written to {output_path}")
            
    except Exception as e:
        print(f"Error generating tableau: {e}")

if __name__ == "__main__":
    solve()
