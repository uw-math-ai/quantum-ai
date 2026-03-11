import stim

def main():
    # Read stabilizers
    with open("my_targets_v2.txt", "r") as f:
        lines = [l.strip().replace(',', '') for l in f if l.strip()]

    # Convert to stim.PauliString
    pauli_stabilizers = []
    for line in lines:
        try:
            pauli_stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
            return

    try:
        t = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    circuit = t.to_circuit(method="graph_state")
    print(circuit)

if __name__ == "__main__":
    main()
