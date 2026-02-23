import stim

def solve():
    with open("stabilizers_49.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Check if we have enough stabilizers for 49 qubits
    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(stabilizers)}")

    # Create tableau from stabilizers
    # allow_underconstrained=True because we might have fewer stabilizers than qubits
    # (though usually for a state we want n stabilizers for n qubits)
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Generate circuit
    circuit = tableau.to_circuit("elimination")
    
    # Save to file
    with open("circuit_49_generated.stim", "w") as f:
        f.write(str(circuit))
    
    print("Circuit generated successfully.")

if __name__ == "__main__":
    solve()
