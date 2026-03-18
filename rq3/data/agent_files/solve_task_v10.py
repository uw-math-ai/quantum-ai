import stim

def solve():
    # Read stabilizers
    try:
        with open('target_stabilizers_v10.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Stabilizer file not found")
        return

    print(f"Read {len(lines)} stabilizers.")

    # Create Tableau from stabilizers
    try:
        # stim.Tableau.from_stabilizers wants a list of strings
        # But we need to make sure they are independent and N stabilizers for N qubits?
        # Or does from_stabilizers handle it?
        # Actually, from_stabilizers expects N stabilizers for N qubits for a full Tableau.
        # If we have fewer, we might need to pad or use a different method.
        # Let's check qubit count based on length.
        num_qubits = len(lines[0])
        print(f"Qubits: {num_qubits}")
        
        # Convert to PauliStrings
        paulis = [stim.PauliString(s) for s in lines]
        
        # Synthesize tableau
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        
        # Synthesize using graph_state method
        # This produces CZs + single qubit gates.
        circuit = tableau.to_circuit(method="graph_state")
        
        # Check metrics
        cx_count = sum(1 for op in circuit if op.name == 'CX')
        cz_count = sum(1 for op in circuit if op.name == 'CZ')
        print(f"Synthesized CX count: {cx_count}")
        print(f"Synthesized CZ count: {cz_count}")
        
        # Save candidate
        with open('candidate.stim', 'w') as f:
            f.write(str(circuit))
            
        print("Candidate saved to candidate.stim")
        
    except Exception as e:
        print(f"Error synthesizing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    solve()
