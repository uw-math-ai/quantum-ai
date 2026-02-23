import stim

def solve():
    with open("stabilizers_37.txt", "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    print(f"Loaded {len(lines)} stabilizers.")
    
    # Create PauliStrings
    stabilizers = [stim.PauliString(s) for s in lines]
    
    # Check commutativity
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Stabilizers {i} and {j} anticommute!")
                return

    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        with open("circuit_37.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit written to circuit_37.stim")
    except Exception as e:
        print(f"Error generating tableau: {e}")

if __name__ == "__main__":
    solve()
