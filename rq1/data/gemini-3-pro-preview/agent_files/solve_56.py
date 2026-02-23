import stim
import sys
import numpy as np

def solve_56(stabilizers_file):
    with open(stabilizers_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    
    # We need 56 independent generators to define a unique state for Tableau algorithm.
    # But we only have 50.
    # We can complete the set with 6 arbitrary Pauli strings that commute with the existing ones
    # and with each other.
    # Or, we can just use the Tableau algorithm with the 50 stabilizers and let it pick the rest?
    # stim.Tableau.from_stabilizers allows underconstrained systems if allow_underconstrained=True.
    
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=False, allow_underconstrained=True)
        # This returns a tableau where the first 50 rows are the stabilizers (or equivalent).
        # Actually, from_stabilizers returns a tableau that prepares the state.
        # If underconstrained, it picks some completion.
        # Let's see if the circuit from this tableau satisfies the stabilizers.
        
        circuit = t.to_circuit()
        print(circuit)
        with open("data/gemini-3-pro-preview/agent_files/circuit_56.stim", "w") as f:
            f.write(str(circuit))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_56(sys.argv[1])
