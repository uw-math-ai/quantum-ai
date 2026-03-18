import stim

def check_commutation(filename):
    with open(filename, 'r') as f:
        content = f.read().strip()
    stabilizers = [stim.PauliString(s.strip()) for s in content.replace('\n', '').split(',') if s.strip()]
    
    print(f"Checking {len(stabilizers)} stabilizers.")
    
    bad_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i+1, len(stabilizers)):
            if stim.PauliString(stabilizers[i]).commutes(stim.PauliString(stabilizers[j])) == False:
                bad_pairs.append((i, j))
                print(f"Anticommute: {i} and {j}")
                
    if not bad_pairs:
        print("All commute.")
    else:
        print(f"Found {len(bad_pairs)} anticommuting pairs.")

if __name__ == "__main__":
    check_commutation("agent_stabilizers.txt")
