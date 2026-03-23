import sys

def load_stabilizers(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    stabs = [line.strip() for line in lines if line.strip()]
    return stabs

def parse_bad_faults(path):
    # Format: Gate 712 (CX on [100, 103]): Fault Z on 100 spreads to 5 data qubits
    faults = []
    with open(path, 'r') as f:
        for line in f:
            if "spreads to" not in line: continue
            # Extract Pauli and Qubit
            # "Fault P on Q"
            parts = line.split("Fault ")[1].split(" spreads")[0]
            pauli, qubit = parts.split(" on ")
            qubit = int(qubit)
            faults.append((pauli, qubit))
    return list(set(faults)) # Unique faults

def get_anti_commuting_stabs(fault, stabilizers):
    pauli, qubit = fault
    matching_indices = []
    for i, s in enumerate(stabilizers):
        # Check commutativity
        # s is a string of I, X, Z, Y
        if qubit >= len(s): continue
        stab_pauli = s[qubit]
        
        # Anti-commute if different and neither is I
        # X, Z anti-commute.
        # X, Y anti-commute.
        # Z, Y anti-commute.
        # X, X commute.
        # X, I commute.
        
        if stab_pauli == 'I': continue
        if pauli == stab_pauli: continue
        
        # If we are here, they are different non-identity.
        # Thus they anti-commute.
        matching_indices.append(i)
    return matching_indices

def solve_set_cover(faults, stabilizers):
    # Greedy approach
    covered_faults = set()
    selected_stabs = []
    
    # Precompute coverage for all stabilizers
    # But only consider those that are low weight?
    # Stabilizers have different weights.
    # Calculate weights.
    stab_weights = []
    for s in stabilizers:
        w = 0
        for char in s:
            if char != 'I': w += 1
        stab_weights.append(w)
        
    # Print weight distribution
    weight_counts = {}
    for w in stab_weights:
        weight_counts[w] = weight_counts.get(w, 0) + 1
    print(f"Weight distribution: {sorted(weight_counts.items())}")

    valid_stabs_indices = [i for i, w in enumerate(stab_weights) if w <= 4]
    print(f"Number of valid stabilizers (weight <= 4): {len(valid_stabs_indices)}")
    
    # Build map: stab_idx -> set of faults it covers
    stab_coverage = {}
    for idx in valid_stabs_indices:
        covered = set()
        for f_idx, f in enumerate(faults):
            if idx in get_anti_commuting_stabs(f, stabilizers):
                covered.add(f_idx)
        stab_coverage[idx] = covered
        
    # Greedy selection
    uncovered_faults = set(range(len(faults)))
    
    while uncovered_faults:
        best_stab = -1
        best_cover_count = -1
        
        for idx in valid_stabs_indices:
            # Count how many NEW faults it covers
            new_cover = stab_coverage[idx].intersection(uncovered_faults)
            count = len(new_cover)
            if count > best_cover_count:
                best_cover_count = count
                best_stab = idx
        
        if best_cover_count <= 0:
            print("Cannot cover all faults with weight <= 4 stabilizers!")
            break
            
        selected_stabs.append(best_stab)
        uncovered_faults -= stab_coverage[best_stab]
        
    return selected_stabs, uncovered_faults

if __name__ == "__main__":
    stabs = load_stabilizers(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt")
    faults = parse_bad_faults(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.txt")
    
    print(f"Total unique bad faults: {len(faults)}")
    
    selected, missing = solve_set_cover(faults, stabs)
    
    print(f"Selected {len(selected)} stabilizers.")
    if missing:
        print(f"Missing {len(missing)} faults.")
    else:
        print("All faults covered.")
        
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\chosen_stabilizers.txt", "w") as f:
        for idx in selected:
            f.write(f"{idx}: {stabs[idx]}\n")
