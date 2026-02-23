import stim
import sys

def solve():
    print("Reading stabilizers...")
    try:
        with open("stabilizers_133.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Loaded {len(lines)} stabilizers")
    if not lines:
        print("No stabilizers found")
        return
    
    n_qubits = len(lines[0])
    print(f"Number of qubits: {n_qubits}")

    # Check length consistency
    for i, line in enumerate(lines):
        if len(line) != n_qubits:
            print(f"Line {i} has length {len(line)}, expected {n_qubits}")
            return

    # Create tableau
    print("Creating tableau...")
    try:
        # Check commutativity first? No, let stim do it.
        # stim.Tableau.from_stabilizers creates a state that stabilizes the given stabilizers.
        # If they are inconsistent, it raises an error.
        # If underconstrained, allow_underconstrained=True fills the rest with arbitrary stabilizers.
        stabilizers = [stim.PauliString(s) for s in lines]
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Failed to create tableau: {e}")
        return

    print("Tableau created. generating circuit...")
    # Create a circuit
    c = t.to_circuit("elimination")
    
    print("Circuit generated. Verifying...")
    # Verify
    sim = stim.TableauSimulator()
    sim.do(c)
    
    # Check against stabilizers
    failed_count = 0
    for i, s_str in enumerate(lines):
        s = stim.PauliString(s_str)
        if not sim.peek_observable_expectation(s) == 1:
            if failed_count < 5:
                print(f"Stabilizer {i} {s_str} not satisfied")
            failed_count += 1
            
    if failed_count > 0:
        print(f"Total failed stabilizers: {failed_count}")
    else:
        print("All stabilizers satisfied.")
        with open("circuit_133.stim", "w") as f:
            f.write(str(c))
        print("circuit_133.stim written.")

if __name__ == "__main__":
    solve()
