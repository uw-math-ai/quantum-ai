import stim
import sys

def solve():
    # Read stabilizers
    with open('stabilizers_105_v2.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Check dimensions
    n_qubits = len(lines[0])
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {len(lines)}")
    
    try:
        stabilizers = [stim.PauliString(s) for s in lines]
        # Using allow_underconstrained=True because we might have fewer stabilizers than qubits
        # Using allow_redundant=True just in case
        t = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = t.to_circuit()
        with open('circuit_105_v2.stim', 'w') as f:
            f.write(str(circuit))
        print("Circuit generated successfully.")
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
