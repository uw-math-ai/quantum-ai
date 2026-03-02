import stim
import sys

def solve():
    try:
        with open("stabilizers_90_v2.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]

        print(f"Number of stabilizers: {len(stabilizers)}")
        
        # Parse stabilizers
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Check lengths
        lengths = set(len(s) for s in pauli_stabilizers)
        print(f"Stabilizer lengths: {lengths}")
        
        # Create tableau
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
        print("Tableau created successfully.")
        
        # Generate circuit
        circuit = tableau.to_circuit("elimination")
        
        # Print the circuit to a file
        with open("circuit_90.stim", "w") as out:
            out.write(str(circuit))
            
        print("Circuit generated and saved to circuit_90.stim")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    solve()

