import stim

def check_commutativity():
    try:
        with open('data/gemini-3-pro-preview/agent_files/stabilizers_135.txt', 'r') as f:
            stabs = [line.strip() for line in f if line.strip()]

        paulis = [stim.PauliString(s) for s in stabs]
        n = len(paulis)
        
        anticommuting_pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                if paulis[i].commutes(paulis[j]) == False:
                    anticommuting_pairs.append((i, j))
        
        print(f"Total stabilizers: {n}")
        print(f"Anticommuting pairs: {len(anticommuting_pairs)}")
        for i, j in anticommuting_pairs[:10]:
            print(f"Stab {i} and Stab {j} anticommute")
            
        if len(anticommuting_pairs) > 0:
            print("Stabilizers are not consistent.")
        else:
            print("Stabilizers are consistent (pairwise commuting).")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_commutativity()
