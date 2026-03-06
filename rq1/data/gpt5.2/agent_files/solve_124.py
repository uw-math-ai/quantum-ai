import stim
import sys

def solve():
    # Read stabilizers from file
    with open('data/stabilizers_124.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Convert to Stim format
    try:
        # Create a Tableau from the stabilizers
        # We need to handle potential over/under-constrained systems or anticommutation
        # But first, let's try the direct method which usually works for these problems
        
        # stim.Tableau.from_stabilizers expects a list of stim.PauliString
        pauli_strings = [stim.PauliString(line) for line in lines]
        
        # Check for consistency/commutativity
        # If there are N qubits, we expect at most N stabilizers
        # If there are more, they must be redundant
        
        # We can use tableau.from_stabilizers with allow_redundant=True and allow_underconstrained=True
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        
        # Convert to circuit using elimination method
        circuit = tableau.to_circuit("elimination")
        
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    solve()
