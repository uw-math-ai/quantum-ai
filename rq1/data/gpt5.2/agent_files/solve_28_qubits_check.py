import stim
import sys

def solve(stabilizers_file):
    with open(stabilizers_file, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Check if they commute
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Anticommuting pair: {i} and {j}")
                # print(f"  {stabilizers[i]}")
                # print(f"  {stabilizers[j]}")
                return

    # Try to generate circuit using Tableau.from_stabilizers
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print(circuit)
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve("stabilizers_28.txt")
