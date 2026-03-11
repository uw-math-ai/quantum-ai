import stim
import sys
import os

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    return lines

def run_synthesis(stabilizers):
    # Create Tableau from stabilizers
    # Note: from_stabilizers expects a list of Pauli strings
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Method 1: Graph State
    try:
        circuit_graph = tableau.to_circuit(method="graph_state")
        
        # Check stats
        # cx_count is 0 for graph state (it uses CZ)
        # We need to verify if it uses other gates that might explode volume
        print(f"Graph State Circuit created.")
        
        # Save to file
        with open("candidate_graph.stim", "w") as f:
            f.write(str(circuit_graph))
            
    except Exception as e:
        print(f"Error in graph state synthesis: {e}")

    # Method 2: Elimination
    try:
        circuit_elim = tableau.to_circuit(method="elimination")
        print(f"Elimination Circuit created.")
        
        with open("candidate_elim.stim", "w") as f:
            f.write(str(circuit_elim))
    except Exception as e:
        print(f"Error in elimination synthesis: {e}")


if __name__ == "__main__":
    stabilizers = read_stabilizers("target_stabilizers_fixed.txt")
    run_synthesis(stabilizers)
