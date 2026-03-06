import stim

def check_commutativity():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_161_fixed.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    stabilizers = [stim.PauliString(line) for line in lines]
    
    print(f"Checking {len(stabilizers)} stabilizers.")
    
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                anticommuting_pairs.append((i, j))
                
    if not anticommuting_pairs:
        print("All stabilizers commute.")
    else:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} vs {j}")
            
if __name__ == "__main__":
    check_commutativity()
