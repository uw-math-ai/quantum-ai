import stim
import sys

def generate_circuit():
    try:
        with open("target_stabilizers_rq3_new_v5.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        stabilizers = [stim.PauliString(l) for l in lines]
        
        # Create tableau from stabilizers
        # allow_redundant=True because the prompt stabilizers might be overcomplete
        # allow_underconstrained=True just in case, though usually we want a full state
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize circuit using graph_state method
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-processing: 
        # The memory mentions replacing RX with H. 
        # Let's inspect if there are any weird gates, but usually graph_state is clean.
        # If the circuit has "RX", it might be a typo for "R" or "MX".
        # But if it works, it works.
        
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    generate_circuit()
