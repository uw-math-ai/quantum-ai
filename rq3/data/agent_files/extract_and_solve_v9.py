import stim
import sys

def solve():
    try:
        # Load baseline
        with open("baseline_v9.stim", "r") as f:
            baseline_text = f.read()
        circuit = stim.Circuit(baseline_text)
        
        # Get number of qubits
        num_qubits = circuit.num_qubits
        print(f"Baseline qubits: {num_qubits}", file=sys.stderr)
        
        # Get tableau from circuit
        tableau = stim.Tableau.from_circuit(circuit)
        
        # Regenerate circuit using graph_state method
        # This usually optimizes CX count heavily (often to 0)
        new_circuit = tableau.to_circuit(method="graph_state")
        
        print(new_circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()
