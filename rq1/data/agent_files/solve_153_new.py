import stim
import sys

def solve():
    # Read stabilizers
    with open('target_stabilizers_153.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers")
    
    # Create the tableau from stabilizers
    # Note: allow_underconstrained=True because we might have fewer stabilizers than qubits 
    # (though usually for a stabilizer state we have n stabilizers for n qubits)
    try:
        # Convert strings to stim.PauliString
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Generate the circuit
    # 'elimination' method uses Gaussian elimination to find a circuit that prepares the state
    circuit = tableau.to_circuit(method="elimination")
    
    # Save the circuit to a file
    with open('solve_153_circuit.stim', 'w') as f:
        f.write(str(circuit))
    
    print("Circuit generated and saved to solve_153_circuit.stim")

if __name__ == "__main__":
    solve()
