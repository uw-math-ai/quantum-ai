import stim
import sys

def solve():
    # Read stabilizers from file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\stabilizers_92.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Parse stabilizers into a Tableau
    # Note: stim.Tableau.from_stabilizers expects a list of stim.PauliString
    pauli_strings = [stim.PauliString(s) for s in stabilizers]
    
    # We want to find a circuit that prepares a state stabilized by these stabilizers.
    # We can use the tableau to find a circuit.
    # However, allow_underconstrained=True is important if the stabilizers don't fully specify the state (e.g. < 92 independent stabilizers).
    # The prompt says "Act on exactly 92 data qubits".
    # There are many stabilizers listed. Let's count them.
    print(f"Number of stabilizers: {len(stabilizers)}")
    print(f"Qubit count: {len(stabilizers[0])}")

    try:
        # allow_redundant=True in case some stabilizers are dependent
        # allow_underconstrained=True in case we have fewer than 92 independent stabilizers
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        
        # Generate the circuit that prepares this state from |0>
        # The 'elimination' method is generally good for this.
        circuit = tableau.to_circuit(method="elimination")
        
        # Verify the circuit
        # We simulate the circuit and check if the stabilizers are satisfied.
        # Ideally, we just output the circuit.
        
        # Print the circuit to a file
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\circuit_92.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")
        # If standard method fails, we might need to debug.

if __name__ == "__main__":
    solve()
