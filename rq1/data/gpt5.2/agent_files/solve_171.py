import stim

def solve():
    with open("stabilizers_171.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Parse stabilizers into stim.PauliString
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    n = len(pauli_stabilizers[0])
    print(f"Number of qubits: {n}")
    for i, s in enumerate(pauli_stabilizers):
        if len(s) != n:
            print(f"Error: Stabilizer {i} has length {len(s)}")

    # Check commutativity
    anticommuting_pairs = []
    for i in range(len(pauli_stabilizers)):
        for j in range(i + 1, len(pauli_stabilizers)):
            if not pauli_stabilizers[i].commutes(pauli_stabilizers[j]):
                anticommuting_pairs.append((i, j))

    print(f"Number of anticommuting pairs: {len(anticommuting_pairs)}")
    if len(anticommuting_pairs) > 0:
        print("Anticommuting pairs (first 10):")
        for p in anticommuting_pairs[:10]:
            print(f"{p}: {stabilizers[p[0]]} vs {stabilizers[p[1]]}")
    else:
        try:
            tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
            circuit = tableau.to_circuit("elimination")
            with open("circuit_171.stim", "w") as f:
                f.write(str(circuit))
            print("Circuit written to circuit_171.stim")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    solve()
