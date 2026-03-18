import stim

def check():
    with open('target_stabilizers_challenge.txt', 'r') as f:
        # Truncate to 92 chars
        lines = [l.strip()[:92] for l in f if l.strip()]
    
    paulis = [stim.PauliString(l) for l in lines]
    
    conflicts = []
    for i in range(len(paulis)):
        for j in range(i+1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                conflicts.append((i, j))
                
    print(f"Found {len(conflicts)} conflicts.")
    for i, j in conflicts:
        print(f"Conflict: {i} vs {j}")

if __name__ == "__main__":
    check()
