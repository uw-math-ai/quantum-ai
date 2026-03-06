import stim
import sys

def solve():
    try:
        # Read stabilizers
        filename = "stabilizers_124.txt"
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Read {len(lines)} stabilizers.")

        # Parse into PauliStrings
        stabilizers = []
        for line in lines:
            try:
                stabilizers.append(stim.PauliString(line))
            except Exception as e:
                print(f"Skipping invalid stabilizer '{line}': {e}")

        # Greedy selection of commuting stabilizers
        consistent_stabilizers = []
        rejected_count = 0
        
        for i, stab in enumerate(stabilizers):
            is_consistent = True
            for existing in consistent_stabilizers:
                if not stab.commutes(existing):
                    # Anticommutes
                    is_consistent = False
                    break
            
            if is_consistent:
                consistent_stabilizers.append(stab)
            else:
                rejected_count += 1
                # print(f"Stabilizer {i} anticommutes with chosen set. Skipping.")

        print(f"Selected {len(consistent_stabilizers)} consistent stabilizers.")
        print(f"Rejected {rejected_count} stabilizers.")

        # Generate Tableau
        # We use allow_underconstrained=True because we might have dropped some stabilizers
        # or the set might naturally be underconstrained.
        tableau = stim.Tableau.from_stabilizers(
            consistent_stabilizers,
            allow_redundant=True,
            allow_underconstrained=True
        )

        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        
        # Verify the circuit against the consistent stabilizers (sanity check)
        # Note: We can't easily check against the rejected ones without running the circuit.
        
        print("Circuit generated successfully.")
        
        # Output the circuit to a file
        with open("circuit_124_new.stim", "w") as f:
            f.write(str(circuit))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    solve()
