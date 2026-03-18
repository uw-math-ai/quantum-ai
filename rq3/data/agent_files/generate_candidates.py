import stim
import sys

def solve():
    print("Loading stabilizers...")
    with open("stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")
    print(f"Number of stabilizers: {len(lines)}")

    # Create Tableau from stabilizers
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines], allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Method 1: Elimination
    print("Generating circuit using elimination method...")
    c_elim = t.to_circuit(method="elimination")
    with open("candidate_elim.stim", "w") as f:
        f.write(str(c_elim))
    
    # Method 2: Graph State
    print("Generating circuit using graph_state method...")
    try:
        c_graph = t.to_circuit(method="graph_state")
        with open("candidate_graph.stim", "w") as f:
            f.write(str(c_graph))
    except Exception as e:
        print(f"Error generating graph state circuit: {e}")

    # Helper: Convert graph state circuit to clean CX/CZ
    # If the circuit uses RX, we might need to handle it.
    
    print("Done.")

if __name__ == "__main__":
    solve()

