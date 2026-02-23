import stim

def check():
    filename = "stabilizers_175.txt"
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"Number of stabilizers: {len(lines)}")
    if len(lines) > 0:
        print(f"Length of first stabilizer: {len(lines[0])}")
    
    # Convert to Stim PauliStrings
    stabilizers = [stim.PauliString(s) for s in lines]
    
    # Check commutativity
    print("Checking commutativity...")
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))
                if len(anticommuting_pairs) > 5:
                    break
        if len(anticommuting_pairs) > 5:
            break
            
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)}+ anticommuting pairs.")
        print(f"First few: {anticommuting_pairs}")
    else:
        print("All stabilizers commute.")

if __name__ == "__main__":
    check()
