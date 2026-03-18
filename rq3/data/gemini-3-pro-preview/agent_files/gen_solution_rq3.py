import stim
import sys

def solve():
    # Read stabilizers
    with open("target_stabilizers_rq3.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    # Create tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs], allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}", file=sys.stderr)
        return

    # Synthesize circuit using graph state method
    # This method naturally produces circuits with H, S, CZ, and single qubit Cliffords.
    # It avoids CX gates, which minimizes the primary metric.
    circuit = t.to_circuit(method="graph_state")
    
    # Check if we need to clean up the circuit (e.g. remove I gates if any, though Stim usually doesn't emit them)
    # Also, verify if 'RX' gates are used (Stim might use them for resets/initialization)
    # but the method="graph_state" usually assumes unitary synthesis from |0>.
    # If the tableau expects inputs, this might be different, but from_stabilizers usually assumes a state preparation.
    
    print(circuit)

if __name__ == "__main__":
    solve()
