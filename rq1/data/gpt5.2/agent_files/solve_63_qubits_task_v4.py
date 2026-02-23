import stim

def solve():
    with open('stabilizers_63_qubits_task_v4.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Try to construct a tableau from stabilizers
    try:
        # Check if the stabilizers are consistent first
        # We can do this by checking commutativity of all pairs
        print(f"Number of stabilizers: {len(stabilizers)}")
        
        # stim.Tableau.from_stabilizers will raise an error if inconsistent
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated successfully.")
        print(circuit)
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
