import stim
import sys

def generate_graph_state_circuit(stabilizers_file, output_file):
    # Read stabilizers
    with open(stabilizers_file, 'r') as f:
        stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]

    # Create tableau
    try:
        # Convert strings to PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize circuit using graph state method
        circuit = tableau.to_circuit(method='graph_state')
        
        # Write to output
        with open(output_file, 'w') as f:
            f.write(str(circuit).replace("RX", "H")) # Simple heuristic if needed, but graph_state usually outputs proper gates.
            # Actually, to_circuit(method='graph_state') produces a circuit that transforms |0> to the state.
            # It uses H, S, CZ, etc.
            # If it uses RX, it means it resets the qubit. But usually it doesn't for pure state prep from |0>.
            # Let's check the output content.
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_graph_state_circuit("target_stabilizers_latest.txt", "candidate_latest.stim")
