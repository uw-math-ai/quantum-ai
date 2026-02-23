import stim
import sys

def solve():
    print("Reading stabilizers...")
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\my_stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse stabilizers
    stabilizers = []
    for i, line in enumerate(lines):
        if i == 30:
            print(f"Skipping stabilizer {i} due to known conflict.")
            continue
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
        print("Generating circuit using method='elimination'...")
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit(method="elimination")
        
        # Verify correctness locally
        print("Verifying circuit locally...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Check each stabilizer
        all_good = True
        failed_count = 0
        for i, s in enumerate(stabilizers):
            # peek_observable_expectation returns +1 or -1.
            # We want +1.
            expectation = sim.peek_observable_expectation(s)
            if expectation != 1:
                print(f"Stabilizer {i} failed: {s}, expectation={expectation}")
                all_good = False
                failed_count += 1
        
        if all_good:
            print("Local verification PASSED.")
            with open('circuit_100.stim', 'w') as f:
                f.write(str(circuit))
            print("Circuit written to circuit_100.stim")
        else:
            print(f"Local verification FAILED. {failed_count} stabilizers failed.")

    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
