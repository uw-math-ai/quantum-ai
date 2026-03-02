import stim

def solve(filename):
    with open(filename, 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")
    pauli_strings = [stim.PauliString(s) for s in stabilizers]
    
    # Verify commutativity
    print("Verifying commutativity...")
    for i in range(len(pauli_strings)):
        for j in range(i + 1, len(pauli_strings)):
            if not pauli_strings[i].commutes(pauli_strings[j]):
                print(f"Stabilizers {i} and {j} anticommute!")
                return

    print("All stabilizers commute.")
    
    # Try to generate circuit
    print("Generating circuit using stim.Tableau.from_stabilizers...")
    try:
        # Create a tableau that stabilizes the state
        # The allow_underconstrained=True is important because we only have 132 stabilizers for 133 qubits
        tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
        
        # Convert to circuit using Gaussian elimination
        circuit = tableau.to_circuit(method="elimination")
        
        # Save circuit
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_133.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit generated and saved to circuit_133.stim")
        
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\my_stabilizers_133.txt")
