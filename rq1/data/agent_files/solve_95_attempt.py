import stim
import sys

def solve():
    print("Reading stabilizers...")
    try:
        with open("stabilizers_95.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print("Error: stabilizers_95.txt not found")
        return

    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(lines)}")

    # Check length
    for i, line in enumerate(lines):
        if len(line) != num_qubits:
            print(f"Error: Line {i} has length {len(line)}, expected {num_qubits}")
            return
            
    # Parse into PauliStrings
    stabilizers = [stim.PauliString(s) for s in lines]

    # Check commutation
    print("Checking commutation...")
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Error: Stabilizers {i} and {j} do not commute!")
                return
    print("All stabilizers commute.")

    # Create tableau from stabilizers
    print("Constructing tableau...")
    try:
        # We want a state |psi> such that S_i |psi> = |psi> for all i.
        # stim.Tableau.from_stabilizers finds a Clifford C such that C |0> is stabilized by the given stabilizers.
        # It requires a full set of N stabilizers for N qubits.
        # If we have fewer, we can pad with dummy Z stabilizers on the remaining degrees of freedom
        # or just ask stim to fill them in.
        
        # Check if we have 95 independent stabilizers.
        # We can use Gaussian elimination to check independence.
        
        # However, stim.Tableau.from_stabilizers supports `allow_underconstrained=True`.
        # It will pick arbitrary stabilizers to complete the set.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # The tableau represents the operation C.
        # Applying C to |00...0> prepares the state.
        # We can get the circuit for C.
        # Use 'elimination' method to decompose into gates
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit constructed.")
        
        # Verify
        print("Verifying circuit...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        all_satisfied = True
        for i, s in enumerate(stabilizers):
            ev = sim.peek_observable_expectation(s)
            if ev != 1:
                print(f"Stabilizer {i} not satisfied. Expectation: {ev}")
                all_satisfied = False
                break
        
        if all_satisfied:
            print("Verification successful!")
            with open("solve_95_circuit.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Verification failed.")
            
    except Exception as e:
        print(f"Error during construction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
