import stim

def check_commutation():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_153.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    paulis = [stim.PauliString(s) for s in lines]
    
    print(f"Checking commutation for {len(paulis)} stabilizers.")
    all_commute = True
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                print(f"Stabilizers {i} and {j} do NOT commute!")
                all_commute = False
                # break/return if you want to stop early
    
    if all_commute:
        print("All stabilizers commute.")
    else:
        print("Some stabilizers anticommute.")

if __name__ == "__main__":
    check_commutation()
