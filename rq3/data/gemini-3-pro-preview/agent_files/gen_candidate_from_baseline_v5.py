import stim
import sys

def main():
    try:
        # Load from the v2 baseline file we just created
        with open('current_baseline_v2.stim', 'r') as f:
            baseline_text = f.read()
        
        circuit = stim.Circuit(baseline_text)
        print(f"Loaded baseline. Num qubits: {circuit.num_qubits}")
        
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Get the inverse tableau
        tableau = sim.current_inverse_tableau().inverse()
        
        # Convert to graph state
        new_circuit = tableau.to_circuit(method='graph_state')
        
        print("Generated circuit stats:")
        print(f"Num qubits: {new_circuit.num_qubits}")
        print(f"Num instructions: {len(new_circuit)}")
        
        with open('candidate_graph_state_v4.stim', 'w') as f:
            f.write(str(new_circuit))
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
