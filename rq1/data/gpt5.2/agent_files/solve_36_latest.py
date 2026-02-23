import stim
import sys

def solve():
    try:
        with open("stabilizers_36_latest.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(stabilizers)} stabilizers.")

        # Convert to stim.PauliString
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Create a tableau from the stabilizers
        # allow_underconstrained=True handles the case where fewer than N stabilizers are provided
        # allow_redundant=True handles the case where some stabilizers are linearly dependent
        t = stim.Tableau.from_stabilizers(
            pauli_stabilizers,
            allow_redundant=True,
            allow_underconstrained=True
        )
        
        # Generate circuit using Gaussian elimination
        circuit = t.to_circuit("elimination")
        
        # Verify the circuit prepares the correct state
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        all_good = True
        failed_count = 0
        for i, s in enumerate(stabilizers):
            # Check if expectation value is +1
            res = sim.peek_observable_expectation(stim.PauliString(s))
            if res != 1:
                print(f"Stabilizer {i} ({s}) failed (expectation {res})")
                failed_count += 1
                all_good = False
        
        if all_good:
            print("All stabilizers verified successfully.")
            with open("circuit_36_latest.stim", "w") as f:
                f.write(str(circuit))
            print("Circuit generated and saved to circuit_36_latest.stim.")
        else:
            print(f"Verification failed. {failed_count} stabilizers failed.")
            
    except Exception as e:
        print(f"Error generating circuit: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
