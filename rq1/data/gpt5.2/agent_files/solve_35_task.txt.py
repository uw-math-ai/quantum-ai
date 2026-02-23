import stim
import sys
import os

def solve():
    with open("stabilizers_35_task.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Check for anticommutativity
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                print(f"Anticommute: {i} and {j}")
                print(f"  {stabilizers[i]}")
                print(f"  {stabilizers[j]}")

    # Try to generate circuit using Tableau.from_stabilizers
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        print("Successfully generated circuit.")
        with open("circuit_35_task.stim", "w") as f:
            f.write(str(circuit))
    except Exception as e:
        print(f"Failed to generate circuit: {e}")

if __name__ == "__main__":
    solve()
