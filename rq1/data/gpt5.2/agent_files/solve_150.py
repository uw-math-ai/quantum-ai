import stim
import sys
import os

def solve(stabilizers_file):
    with open(stabilizers_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # There are 150 qubits
    num_qubits = 150
    
    # Check if we have enough stabilizers
    print(f"Number of stabilizers: {len(stabilizers)}")
    
    # Try to generate a tableau from the stabilizers
    try:
        # allow_redundant=True handles linearly dependent stabilizers (as long as they are consistent)
        # allow_underconstrained=True handles fewer than 150 independent stabilizers (qubits left in mixed state or arbitrary)
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        # If successful, convert to circuit
        circuit = tableau.to_circuit("elimination")
        print("Successfully generated circuit.")
        
        # Verify
        # We can verify locally using stim
        # Create a TableauSimulator
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Check if the state satisfies the stabilizers
        all_good = True
        for s in stabilizers:
            # Measure expectation value
            # Since it's a stabilizer state, expectation should be +1 or -1
            # We want +1.
            # However, stim's measure_expectation returns the expectation value.
            # But simpler is to check if it's a stabilizer.
            if not sim.peek_observable_expectation(s) == 1:
                print(f"Failed for stabilizer: {s}")
                all_good = False
                break
        
        if all_good:
            print("Verification passed locally.")
            with open("circuit_150.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Verification failed locally.")

    except Exception as e:
        print(f"Error generating tableau: {e}")

if __name__ == "__main__":
    solve("stabilizers_150.txt")
