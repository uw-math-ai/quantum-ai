import stim

def solve():
    try:
        with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_102.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = lines
        
        # Verify number of qubits
        num_qubits = len(stabilizers[0])
        print(f"Number of qubits: {num_qubits}")
        print(f"Number of stabilizers: {len(stabilizers)}")

        # Convert strings to PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Create Tableau from stabilizers
        # allow_underconstrained=True because we might have fewer than N stabilizers
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
        
        # Convert to circuit
        circuit = tableau.to_circuit()
        
        # Save circuit to file
        with open(r"data\gemini-3-pro-preview\agent_files\circuit_102.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
