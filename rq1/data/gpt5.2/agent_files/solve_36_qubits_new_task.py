import stim

stabilizers = [
    "XXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXIXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXIXXIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIII",
    "IIIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIXXIXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIXXIXXIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXX",
    "IIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIII",
    "IIIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXII",
    "IIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZI",
    "IZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIII",
    "ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII",
    "IIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ",
    "IIXXXIIIIIIXXXIIIIIIXXXIIIIIIXXXIIII",
    "ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII"
]

def solve():
    print("Starting solver...")
    # Convert strings to stim.PauliString
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

    # Try to generate a tableau from the stabilizers
    try:
        # Check for anticommutativity first to be safe
        for i in range(len(pauli_stabilizers)):
            for j in range(i + 1, len(pauli_stabilizers)):
                if not pauli_stabilizers[i].commutes(pauli_stabilizers[j]):
                    print(f"Anticommuting pair found: {i} and {j}")
                    # return

        print("Creating tableau...")
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
        print("Tableau created. Generating circuit...")
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated.")
        
        with open("circuit_36_new.stim", "w") as f:
            print(circuit, file=f)
        print("Circuit written to circuit_36_new.stim")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
