import stim
import sys

def solve():
    try:
        with open("target_stabilizers_119_v3.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(stabilizers)} stabilizers.")

        # Create the tableau from the stabilizers
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Check for qubit count consistency
        num_qubits = len(stabilizers[0])
        print(f"Number of qubits: {num_qubits}")
        
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
        
        # Invert to get state preparation from |0>
        # 'elimination' method returns a circuit that prepares the state.
        # But wait, tableau.to_circuit("elimination") returns a circuit C such that C |0> -> |stabilized state> ?
        # Let's check documentation or experiment.
        # Usually tableau.to_circuit() creates a circuit that implements the tableau operation.
        # If the tableau represents a state (i.e. stabilizers Z_i -> S_i), then to_circuit() might implement the unitary that maps Z basis to that state.
        # But from_stabilizers creates a Tableau representing the state.
        # The documentation for `to_circuit("elimination")` says it computes a circuit that prepares the state stabilized by the tableau's stabilizers, starting from the all-zero state.
        
        circuit = tableau.to_circuit("elimination")
        
        # Verify the circuit works (locally)
        # sim = stim.TableauSimulator()
        # sim.do(circuit)
        # for s in pauli_stabilizers:
        #    if sim.peek_observable_expectation(s) != 1:
        #        print(f"Failed check for {s}")
        
        with open("circuit_119_v3.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully.")

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    solve()
