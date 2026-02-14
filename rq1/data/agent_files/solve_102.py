import stim

def solve():
    with open("target_stabilizers_102.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        # Remove line numbers if present (e.g. "1. IIIX...")
        if ". " in line:
            line = line.split(". ")[1]
        stabilizers.append(stim.PauliString(line))

    # Create tableau
    # allow_underconstrained=True allows fewer stabilizers than qubits
    # It will pick a state that satisfies the stabilizers.
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        # If allow_underconstrained is not supported or other error
        # Try finding a state manually if needed, but stim usually supports this.
        return

    # Convert to circuit
    # method="elimination" is usually good.
    circuit = tableau.to_circuit(method="elimination")

    with open("circuit_102.stim", "w") as f:
        f.write(str(circuit))

if __name__ == "__main__":
    solve()
