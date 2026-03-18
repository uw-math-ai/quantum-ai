import stim
import sys

def solve():
    stabilizers_str = [
        "XXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIXXIXXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIXXIXXIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIII",
        "IIIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIXXIXXIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIXXIXXIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXX",
        "IIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIII",
        "IIIXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXII",
        "IIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZI",
        "IZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIII",
        "ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII",
        "IIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ",
        "IIXXXIIIIIIXXXIIIIIIXXXIIIIIIXXXIIII", "ZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZIIZII"
    ]

    try:
        # Convert strings to PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers_str]
        
        # Create tableau
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize circuit using graph_state method
        circuit = tableau.to_circuit(method="graph_state")
        
        # Replace RX with H, assuming initialization from |0>
        # We need to construct a new circuit manually to iterate and print cleanly
        
        # Helper to clean and print
        for instruction in circuit:
            if instruction.name == "RX":
                # Replace RX with H
                targets = instruction.targets_copy()
                # Print H with targets
                t_str = " ".join(str(t.value) for t in targets)
                print(f"H {t_str}")
            elif instruction.name == "CZ":
                # Split CZ into smaller chunks
                targets = instruction.targets_copy()
                # Targets are pairs for CZ? No, CZ can take multiple targets in a sequence
                # CZ 0 1 2 3 means CZ 0 1 and CZ 2 3
                # So we must take pairs
                for i in range(0, len(targets), 2):
                    t1 = targets[i].value
                    t2 = targets[i+1].value
                    print(f"CZ {t1} {t2}")
            else:
                print(instruction)

        # We don't need to write to file if we print clean lines
        # But let's verify

        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()
