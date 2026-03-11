import stim
import sys

def solve():
    with open("target_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    stabilizers = [stim.PauliString(l) for l in lines]
    if not stabilizers:
        print("No stabilizers found", file=sys.stderr)
        return

    num_qubits = len(stabilizers[0])
    print(f"Number of qubits: {num_qubits}", file=sys.stderr)
    print(f"Number of stabilizers: {len(stabilizers)}", file=sys.stderr)

    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}", file=sys.stderr)
        return

    circuit = tableau.to_circuit(method="graph_state")
    print(circuit)

if __name__ == "__main__":
    solve()
