import stim

def check_commutation():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\stabilizers_92.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    paulis = [stim.PauliString(s) for s in stabilizers]
    
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if paulis[i].commutes(paulis[j]) == False:
                anticommuting_pairs.append((i, j))
                
    if not anticommuting_pairs:
        print("All stabilizers commute.")
    else:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} and {j} anticommute")
            
    # If they anticommute, we can't satisfy all.
    # Maybe there is a typo in the prompt or I copied it wrong?
    # Or maybe some are redundant/conflicting?
    
if __name__ == "__main__":
    check_commutation()
