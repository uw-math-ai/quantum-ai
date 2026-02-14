import stim
import sys

def solve():
    # Read stabilizers
    with open('stabilizers_105.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Check dimensions
    n_qubits = len(lines[0])
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {len(lines)}")
    
    # Create tableau from stabilizers
    # stim.Tableau.from_stabilizers expects a list of stabilizers that are independent and commuting.
    # The stabilizers provided might not be a complete set for 105 qubits, but they define the state.
    # If they are fewer than 105, we have degrees of freedom.
    # If they are exactly 105, it is a unique state.
    
    # We want to find a circuit that prepares the state.
    # If we use stim.Tableau.from_stabilizers(lines), it returns a tableau T such that T|0> has the given stabilizers.
    # Note: allow_redundant=True might be needed if there are redundant generators.
    # allow_underconstrained=True might be needed if fewer than n generators.
    
    try:
        stabilizers = [stim.PauliString(s) for s in lines]
        t = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = t.to_circuit()
        with open('circuit_105.stim', 'w') as f:
            f.write(str(circuit))
        print("Circuit generated successfully.")
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
