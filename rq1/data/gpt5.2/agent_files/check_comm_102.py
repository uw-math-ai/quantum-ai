import stim

def check_structure():
    with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_102.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Convert to PauliStrings
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    # Check for anticommutativity
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if stim.PauliString.commutes(paulis[i], paulis[j]) == False:
                anticommuting_pairs.append((i, j))
                
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} and {j}")
    else:
        print("All stabilizers commute.")

    # Check for dependencies
    # We can use Gaussian elimination logic or just try to add them one by one to a Tableau
    # and see if they are independent.
    
    t = stim.Tableau(len(stabilizers[0]))
    # This is a bit complex to implement manually efficiently.
    # But since stim.Tableau.from_stabilizers didn't error, they commute.
    
    # Let's check if the failed ones are the last ones or specific ones.
    # The failed ones are line 72 and line 96 (0-indexed: 71 and 95)
    # But line numbers in view started at 1. So indices 71 and 95.
    
    idx_1 = 71
    idx_2 = 95
    
    failed_1 = stabilizers[idx_1]
    failed_2 = stabilizers[idx_2]
    
    print(f"Checking dependencies for stabilizer {idx_1}: {failed_1}")
    print(f"Checking dependencies for stabilizer {idx_2}: {failed_2}")

    # Check commutativity of these specific ones against all others
    for i in [idx_1, idx_2]:
        for j, s in enumerate(stabilizers):
            if i == j: continue
            if not stim.PauliString.commutes(paulis[i], paulis[j]):
                print(f"Stabilizer {i} anticommutes with {j}")

if __name__ == "__main__":
    check_structure()
