import stim
import numpy as np

stabilizers_str = [
    "XXXXXXXXIIIIIII",
    "IXXIXXIIXXIXXII",
    "IIXXIXXIIXXXIXI",
    "IIIIXXXXIIIXXXX",
    "ZZZZIIIIIIIIIII",
    "IZZIZZIIIIIIIII",
    "IIZZIZZIIIIIIII",
    "IIIIZZZZIIIIIII",
    "IZIIZIIIZIIIZII",
    "IIZIIZIIIZIZIII",
    "IIZZIIIIIZZIIII",
    "IIIIZZIIIIIZZII",
    "IIIIIZZIIIIZIZI",
    "IIIIIIZZIIIIIZZ"
]

stabilizers = [stim.PauliString(s) for s in stabilizers_str]

def check_commutativity(stabs):
    n = len(stabs)
    comm_matrix = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if not stabs[i].commutes(stabs[j]):
                comm_matrix[i, j] = 1
                comm_matrix[j, i] = 1
                print(f"Stabilizer {i} and {j} anticommute")
    return comm_matrix

print("Checking commutativity...")
check_commutativity(stabilizers)

try:
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    print("\nStim Tableau created successfully")
    circuit = tableau.to_circuit("elimination")
    print("Circuit generated successfully")
    with open("data/gemini-3-pro-preview/agent_files/circuit_15.stim", "w") as f:
        f.write(str(circuit))
except Exception as e:
    print(f"\nError creating tableau: {e}")
