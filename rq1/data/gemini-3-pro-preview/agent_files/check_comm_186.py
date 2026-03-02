import stim
import sys

def check_comm():
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186_clean.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Checking commutativity for {len(stabilizers)} stabilizers...")
    
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
                if len(anticommuting_pairs) < 10:
                    print(f"Anticommuting pair: {i} and {j}")
                    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
    else:
        print("All stabilizers commute.")

if __name__ == "__main__":
    check_comm()
