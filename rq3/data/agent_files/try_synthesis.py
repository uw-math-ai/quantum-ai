import stim

def generate_circuit():
    try:
        with open("target_stabilizers_prompt.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        # Create a tableau from the stabilizers
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
        
        # Synthesize a circuit using graph state method
        circuit = tableau.to_circuit(method="graph_state")
        
        # Convert to string
        circuit_str = str(circuit)
        
        # Replace RX with H (assuming start state is |0>)
        # Note: RX resets to |+>. H|0> = |+>.
        # We only replace if it's at the start or we are sure it's initialization.
        # But graph_state usually puts initialization at the start.
        circuit_str = circuit_str.replace("RX", "H")
        
        # Remove TICKs
        circuit_str = circuit_str.replace("TICK\n", "")
        
        # Write to file
        with open("candidate.stim", "w") as f:
            f.write(circuit_str)
        
        print("Candidate written to candidate.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_circuit()
