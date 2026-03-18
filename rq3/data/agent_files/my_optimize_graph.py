import stim
import sys

def optimize_to_graph_state():
    try:
        # Load baseline
        with open("baseline.stim", "r") as f:
            circuit = stim.Circuit(f.read())
        
        # Convert to tableau
        tableau = circuit.to_tableau()
        
        # Convert to graph state circuit
        # This will use CZ gates and H gates.
        graph_circuit = tableau.to_circuit(method="graph_state")
        
        # Output the result
        with open("candidate.stim", "w") as f:
            f.write(str(graph_circuit))
        print(f"Wrote candidate to candidate.stim")
        print(f"Candidate length: {len(graph_circuit)}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    optimize_to_graph_state()
