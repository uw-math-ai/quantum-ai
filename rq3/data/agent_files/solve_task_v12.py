import stim
import sys

def solve():
    try:
        # Load baseline
        with open("baseline_v12.stim", "r") as f:
            baseline_text = f.read()
        circuit = stim.Circuit(baseline_text)
        
        print(f"Baseline loaded. Qubits: {circuit.num_qubits}", file=sys.stderr)
        
        # Method 1: Use tableau from baseline circuit
        # This guarantees we preserve the baseline's stabilizers (assuming baseline is correct)
        tableau = stim.Tableau.from_circuit(circuit)
        
        # Synthesize using graph_state method (optimized for CX count)
        new_circuit = tableau.to_circuit(method="graph_state")
        
        # Write to candidate file
        with open("candidate_v12.stim", "w") as f:
            f.write(str(new_circuit))
            
        print("Candidate generated in candidate_v12.stim", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    solve()
