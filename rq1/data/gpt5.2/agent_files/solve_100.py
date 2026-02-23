import stim
import sys

def solve():
    with open('stabilizers_100.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing stabilizer '{line}': {e}")
            sys.exit(1)

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Create tableau from stabilizers
    try:
        # allow_underconstrained=True because we might not have a full set of N stabilizers for N qubits
        # but we want a state that satisfies all of them.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit(method="elimination")
        
        # Verify correctness locally
        # Simulate the circuit.
        # Initialize to |0>.
        # Apply circuit.
        # Measure stabilizers. They should all be +1 (result False in check_stabilizers terminology usually, 
        # but stim's measure_observables returns True for -1 and False for +1? 
        # Actually let's use TableauSimulator.
        
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Check each stabilizer
        all_good = True
        for i, s in enumerate(stabilizers):
            # peek_observable_expectation returns +1 or -1.
            # We want +1.
            expectation = sim.peek_observable_expectation(s)
            if expectation != 1:
                print(f"Stabilizer {i} failed: {s}, expectation={expectation}")
                all_good = False
        
        if all_good:
            print("Local verification PASSED.")
            with open('circuit_100.stim', 'w') as f:
                f.write(str(circuit))
        else:
            print("Local verification FAILED.")

    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
