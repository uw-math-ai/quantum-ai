import stim

def check_commutativity():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_81_qubits.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(s) for s in lines]
    
    failed_indices = []
    # I know which ones failed from the previous tool output, but let's find them by string matching if I can
    # actually I'll just check all pairs.
    
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                anticommuting_pairs.append((i, j))
                print(f"Stabilizers {i} and {j} anticommute!")

    if not anticommuting_pairs:
        print("All stabilizers commute.")
    else:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")

if __name__ == "__main__":
    check_commutativity()
