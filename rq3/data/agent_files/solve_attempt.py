import stim

def solve():
    # Read stabilizers
    with open('current_task_stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Create tableau
    try:
        # Convert strings to PauliStrings explicitly just in case
        pauli_strings = [stim.PauliString(s) for s in lines]
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        try:
             # Try without explicit conversion if the above fails (though unlikely)
             tableau = stim.Tableau.from_stabilizers(lines, allow_redundant=True, allow_underconstrained=True)
        except Exception as e2:
             print(f"Error creating tableau (2nd attempt): {e2}")
             return

    # Synthesis method 'graph_state' is good for CX count (uses CZ)
    try:
        circuit = tableau.to_circuit(method='graph_state')
        # Check if RX are present. If so, and we want to preserve |0> initialization behavior...
        # Actually, let's just print it and check with evaluate_optimization
        print(circuit)
    except Exception as e:
        print(f"Error synthesizing circuit: {e}")

if __name__ == "__main__":
    solve()
