import stim

def solve():
    with open("stabilizers_84.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Generate circuit
    circuit = tableau.to_circuit(method="elimination")
    circuit.to_file("circuit_84.stim")
    print("Circuit saved to circuit_84.stim")

if __name__ == "__main__":
    solve()
