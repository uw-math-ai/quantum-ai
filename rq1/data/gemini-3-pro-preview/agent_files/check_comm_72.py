import stim

def check_commutativity():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\my_stabilizers_72.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if paulis[i].commutes(paulis[j]) == False:
                anticommuting_pairs.append((i, j))
                print(f"Stabilizers {i} and {j} anticommute:")
                print(f"  {stabilizers[i]}")
                print(f"  {stabilizers[j]}")
    
    if not anticommuting_pairs:
        print("All stabilizers commute.")
    else:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")

if __name__ == "__main__":
    check_commutativity()
