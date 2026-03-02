import stim

def solve():
    with open("stabilizers_35_v2.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line: {line}")
            continue

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Check commutativity
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))

    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs:")
        for i, j in anticommuting_pairs[:10]:
            print(f"  {i} and {j}")
            print(f"  {stabilizers[i]}")
            print(f"  {stabilizers[j]}")
        if len(anticommuting_pairs) > 10:
            print("  ...")
    else:
        print("All stabilizers commute.")

    # Try to solve
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        print("Circuit generation successful!")
        with open("circuit_35_generated.stim", "w") as f:
            f.write(str(circuit))
    except Exception as e:
        print(f"Circuit generation failed: {e}")

if __name__ == "__main__":
    solve()
