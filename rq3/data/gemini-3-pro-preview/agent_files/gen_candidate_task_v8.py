import stim
import sys

def solve():
    # Load stabilizers from file
    with open("current_task_stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    # Convert to Stim Tableau
    try:
        # Create PauliStrings
        pauli_stabs = [stim.PauliString(s) for s in stabs]
        
        # Use allow_redundant=True and allow_underconstrained=True to be safe
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize using graph_state method
        # This usually produces H + CZ + Cliffords, which has 0 CX gates
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process to remove any unnecessary instructions if present (though graph_state is usually clean)
        # Also, graph_state might use RX, but we prefer H for initialization if starting from 0. 
        # But here we are just outputting the circuit.
        # The prompt says: "Do NOT introduce measurements, resets, or noise unless they already exist in the baseline"
        # The synthesized circuit shouldn't have them unless the stabilizers imply them (unlikely for this problem).
        
        # Optimizing the circuit slightly to remove adjacent inverse gates if any
        # But Stim's synthesis is usually good.
        
        # Output the circuit
        print(circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    solve()
