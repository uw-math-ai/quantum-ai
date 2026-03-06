import stim
import sys

stabilizers = [
    "XXIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXIIXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXIIXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXIIXXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIXXI",
    "XIXIXIXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXIXIXIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXIXIXIXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIXIXIXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXIX",
    "IIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXX",
    "ZZIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIZZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIZZI",
    "ZIZIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZIZIZIZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZIZIZIZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIZIZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZIZ",
    "IIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZ",
    "XXXIIIIZZZIIIIZZZIIIIXXXIIIIIIIIIII",
    "IIIIIIIXXXIIIIZZZIIIIZZZIIIIXXXIIII",
    "XXXIIIIIIIIIIIXXXIIIIZZZIIIIZZZIIII",
    "ZZZIIIIXXXIIIIIIIIIIIXXXIIIIZZZIIII"
]

def check_commutativity(stabs):
    paulis = [stim.PauliString(s) for s in stabs]
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
    return anticommuting_pairs

def solve():
    print(f"Number of stabilizers: {len(stabilizers)}")
    print(f"Number of qubits: {len(stabilizers[0])}")

    anticommuting = check_commutativity(stabilizers)
    if anticommuting:
        print(f"Found {len(anticommuting)} anticommuting pairs:")
        for i, j in anticommuting[:10]:
            print(f"  {i} and {j}")
        if len(anticommuting) > 10:
            print("  ...")
    else:
        print("All stabilizers commute.")

    try:
        pauli_stabs = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        with open("circuit_35_task.stim", "w") as f:
            f.write(str(circuit))
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
