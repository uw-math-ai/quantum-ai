import stim

def solve():
    with open("stabilizers_186.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Create the tableau from stabilizers
    # Note: stim expects a list of PauliString objects
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Create the tableau
    # allow_underconstrained=True because we might have fewer stabilizers than qubits
    # (though usually for a stabilizer state we have N stabilizers for N qubits,
    #  but sometimes we are given generators that might be redundant or not full rank,
    #  although for a pure state it should be full rank. 'elimination' method handles this.)
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize the circuit
    circuit = tableau.to_circuit(method="elimination")

    # Output the circuit
    print(circuit)

if __name__ == "__main__":
    solve()
