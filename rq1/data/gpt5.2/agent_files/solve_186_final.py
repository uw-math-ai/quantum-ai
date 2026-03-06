import stim

def solve():
    with open("stabilizers_186.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Fix line 105 (index 105)
    # It has length 184, should be 186.
    # We found it needs 2 'I's prepended.
    if len(lines[105]) == 184:
        lines[105] = "II" + lines[105]
        print("Fixed stabilizer 105 length.")
    
    # Verify all lengths
    for i, line in enumerate(lines):
        if len(line) != 186:
            print(f"Error: Stabilizer {i} has length {len(line)}")
            return

    stabilizers = [stim.PauliString(line) for line in lines]
    
    # Verify commutativity
    bad_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i+1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                bad_pairs.append((i, j))
    
    print(f"Anticommutes: {len(bad_pairs)}")
    if bad_pairs:
        return

    # Solve
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit(method="elimination")
        
        # Save to file
        with open("circuit_186_final.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit generated.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
