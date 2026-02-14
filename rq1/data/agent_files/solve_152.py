import stim
import sys

def solve():
    # Read stabilizers
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\target_stabilizers_152.txt') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Convert to stim.PauliString
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

    # Create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Convert to circuit
    circuit = tableau.to_circuit()

    # Verify the circuit
    # We can use the check_stabilizers_tool, but let's first check locally if possible.
    # But for now, let's just output the circuit to a file.
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_solution_152.stim', 'w') as f:
        f.write(str(circuit))
    
    print("Circuit generated successfully.")

if __name__ == "__main__":
    solve()
