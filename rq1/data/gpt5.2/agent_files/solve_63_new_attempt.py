import stim
import sys

def solve():
    try:
        # Load stabilizers
        with open("stabilizers_63_qubits.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        paulis = [stim.PauliString(s) for s in stabilizers]
        
        # Check commutativity
        anticommuting_pairs = []
        for i in range(len(paulis)):
            for j in range(i + 1, len(paulis)):
                if not paulis[i].commutes(paulis[j]):
                    anticommuting_pairs.append((i, j))
        
        if anticommuting_pairs:
            print(f"WARNING: {len(anticommuting_pairs)} pairs of stabilizers anticommute.")
            print(f"First 5 pairs: {anticommuting_pairs[:5]}")
        
        # Try to create a tableau
        try:
            # We use allow_underconstrained=True to handle cases where we have fewer stabilizers than qubits
            # We use allow_redundant=True to handle redundant stabilizers (linearly dependent)
            # We use allow_os_is_es=True just in case
            tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
            circuit = tableau.to_circuit("elimination")
            print("Circuit generated successfully.")
            
            # Verify the circuit locally
            sim = stim.TableauSimulator()
            sim.do(circuit)
            
            preserved = 0
            failed_indices = []
            for i, s in enumerate(stabilizers):
                p = stim.PauliString(s)
                # We need to measure the stabilizer
                # If the measurement outcome is +1 (0 in stim measurement result), it is preserved.
                # Wait, stim measures return 0 for +1 and 1 for -1?
                # Let's check: measure_observable returns expected value.
                # If deterministic, returns +1 or -1.
                expectation = sim.peek_observable_expectation(p)
                if expectation == 1:
                    preserved += 1
                else:
                    failed_indices.append(i)
            
            print(f"Preserved {preserved}/{len(stabilizers)} stabilizers.")
            if failed_indices:
                 print(f"Failed indices (first 10): {failed_indices[:10]}")

            # Save the circuit
            with open("circuit_63_new.stim", "w") as f:
                f.write(str(circuit))
                
        except Exception as e:
            print(f"Error creating tableau: {e}")
            import traceback
            traceback.print_exc()
            return

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
