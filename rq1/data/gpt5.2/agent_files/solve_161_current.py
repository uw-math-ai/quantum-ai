import stim
import os

def solve():
    # Absolute path to the stabilizers file
    stabilizers_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_161_current.txt"
    if not os.path.exists(stabilizers_path):
        print(f"Error: {stabilizers_path} does not exist.")
        return

    with open(stabilizers_path, "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Read {len(stabilizers)} stabilizers.")

    # Convert to Stim PauliStrings
    try:
        pauli_strings = [stim.PauliString(s) for s in stabilizers]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return

    # Check for commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(pauli_strings)):
        for j in range(i + 1, len(pauli_strings)):
            if not pauli_strings[i].commutes(pauli_strings[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        
        # Count conflicts
        conflict_counts = {}
        for i, j in anticommuting_pairs:
            conflict_counts[i] = conflict_counts.get(i, 0) + 1
            conflict_counts[j] = conflict_counts.get(j, 0) + 1
            
        removed_indices = set()
        while anticommuting_pairs:
            # Find the stabilizer with the most remaining conflicts
            best_candidate = -1
            max_conflicts = -1
            
            current_counts = {}
            for i, j in anticommuting_pairs:
                 current_counts[i] = current_counts.get(i, 0) + 1
                 current_counts[j] = current_counts.get(j, 0) + 1
            
            if not current_counts:
                break
                
            best_candidate = max(current_counts, key=current_counts.get)
            
            print(f"Removing stabilizer {best_candidate} (involved in {current_counts[best_candidate]} pairs)")
            removed_indices.add(best_candidate)
            
            # Remove pairs involved with this candidate
            anticommuting_pairs = [(i, j) for i, j in anticommuting_pairs if i != best_candidate and j != best_candidate]
            
        print(f"Removing {len(removed_indices)} stabilizers: {sorted(list(removed_indices))}")
        
        valid_pauli_strings = [s for k, s in enumerate(pauli_strings) if k not in removed_indices]
    else:
        print("All stabilizers commute.")
        valid_pauli_strings = pauli_strings

    # Try to generate circuit
    try:
        # allow_underconstrained=True because we might not have 161 independent stabilizers
        tableau = stim.Tableau.from_stabilizers(valid_pauli_strings, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        
        # Absolute path for output
        output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_161_current.stim"
        with open(output_path, "w") as f:
            f.write(str(circuit))
        print(f"Circuit written to {output_path}")
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
