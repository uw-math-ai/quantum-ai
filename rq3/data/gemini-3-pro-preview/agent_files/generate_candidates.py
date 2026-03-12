import stim

def generate_graph_state_circuit(stabilizers_path, output_path, method='graph_state'):
    with open(stabilizers_path, 'r') as f:
        lines = f.readlines()
    
    stabilizers = [line.strip().replace(',', '') for line in lines if line.strip()]
    
    # Create tableau
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        print(f"Number of stabilizers: {len(pauli_stabilizers)}")
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit
    try:
        circuit = tableau.to_circuit(method=method)
    except Exception as e:
        print(f"Error synthesizing circuit with method {method}: {e}")
        return

    with open(output_path, 'w') as f:
        f.write(str(circuit))
    
    print(f"Generated {output_path} using method {method}")
    
    # Also print some stats
    print(f"Stats for {method}:")
    print(f"  Num gates: {len(circuit)}")
    print(f"  Num qubits: {circuit.num_qubits}")

if __name__ == "__main__":
    generate_graph_state_circuit('target_stabilizers.txt', 'candidate_graph.stim', method='graph_state')
    generate_graph_state_circuit('target_stabilizers.txt', 'candidate_elimination.stim', method='elimination')
