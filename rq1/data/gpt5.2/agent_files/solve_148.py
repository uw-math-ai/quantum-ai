import stim

def solve():
    with open("stabilizers_148.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Convert stabilizers to stim.Tableau
    # We use from_stabilizers with stim.PauliString
    
    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(lines)}")
    
    # Try to Create a tableau from the stabilizers
    try:
        pauli_strings = [stim.PauliString(s) for s in lines]
        t = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        c = t.to_circuit("elimination")
        print("Successfully generated circuit using elimination.")
        with open("circuit_generated.stim", "w") as f:
            f.write(str(c))
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
