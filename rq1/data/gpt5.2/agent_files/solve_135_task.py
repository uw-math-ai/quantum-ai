import stim
import sys

def solve():
    try:
        with open("stabilizers_135.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]

        print(f"Number of stabilizers: {len(lines)}")
        if not lines:
            print("No stabilizers found!")
            return

        L = len(lines[0])
        print(f"Qubit count (from length): {L}")
        
        for i, line in enumerate(lines):
            if len(line) != L:
                print(f"Error: Stabilizer {i} has length {len(line)}, expected {L}")
                return

        # Create PauliStrings
        paulis = [stim.PauliString(line) for line in lines]

        # Try to create tableau
        # Using allow_redundant=True in case there are dependent generators
        # Using allow_underconstrained=True just in case, but we should check if we have L stabilizers for L qubits
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        
        print(f"Tableau created successfully.")
        
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated successfully.")
        
        # Verify the circuit prepares the state
        # We can simulate it.
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        print("Verifying stabilizers...")
        all_good = True
        for i, p in enumerate(paulis):
            # measure_expectation returns +1 or -1. We want +1.
            # actually peek_observable_expectation
            exp = sim.peek_observable_expectation(p)
            if exp != 1:
                print(f"Stabilizer {i} failed: expectation {exp}")
                all_good = False
                break
        
        if all_good:
            print("All stabilizers verified locally!")
            with open("circuit_135_solution.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Verification failed.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
