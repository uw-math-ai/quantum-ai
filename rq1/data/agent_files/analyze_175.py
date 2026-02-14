import stim

def analyze():
    with open('stabilizers_175.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if not lines:
        print("No stabilizers found.")
        return

    n_qubits = len(lines[0])
    n_stabilizers = len(lines)
    
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {n_stabilizers}")
    
    # Check if all have same length
    for i, line in enumerate(lines):
        if len(line) != n_qubits:
            print(f"Stabilizer {i} has length {len(line)}, expected {n_qubits}")
            
    # Try to form a tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in lines], allow_underconstrained=True)
        print("Tableau creation successful.")
        print(f"Tableau shape: {t.shape}")
        
        # Generate circuit
        circuit = t.to_circuit("elimination")
        print("Circuit generation successful.")
        
        with open('circuit_175.stim', 'w') as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    analyze()
