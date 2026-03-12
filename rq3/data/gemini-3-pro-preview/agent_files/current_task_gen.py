import stim
import sys

def main():
    try:
        # Load the baseline circuit
        with open('current_task_baseline.stim', 'r') as f:
            baseline_text = f.read()
        
        circuit = stim.Circuit(baseline_text)
        
        # Convert to tableau
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Get the tableau that creates the state from |0>
        tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize a new circuit using graph state method
        # This uses H, S, CZ, etc. to create the state.
        # It guarantees cx_count = 0 (as it uses CZ).
        new_circuit = tableau.to_circuit(method='graph_state')
        
        # Output the new circuit
        print(new_circuit)
        
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
