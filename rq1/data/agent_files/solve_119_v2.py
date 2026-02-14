import stim
import sys

def solve():
    with open("target_stabilizers_119_v2.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Create the tableau from the stabilizers
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    except Exception as e:
        sys.stderr.write(f"Error creating tableau: {e}\n")
        sys.exit(1)

    # Invert to get state preparation from |0>
    circuit = tableau.to_circuit("elimination").inverse()
    print(circuit)

if __name__ == "__main__":
    solve()
