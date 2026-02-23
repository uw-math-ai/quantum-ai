import stim
import sys

def solve():
    # Read stabilizers from file
    print("Reading stabilizers from file...")
    try:
        with open(r'data\gemini-3-pro-preview\agent_files\stabilizers_125.txt', 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Stabilizer file not found.")
        return

    print(f"Loaded {len(stabilizers)} stabilizers.")
    if not stabilizers:
        print("No stabilizers found!")
        return

    n_qubits = len(stabilizers[0])
    print(f"Number of qubits: {n_qubits}")

    # Check consistency
    for i, s in enumerate(stabilizers):
        if len(s) != n_qubits:
            print(f"Error: Stabilizer {i} has length {len(s)}, expected {n_qubits}")
            return

    # Check for anticommuting pairs first
    if not check_commutativity(stabilizers):
        print("Found anticommuting pairs! This indicates a problem with the stabilizers.")
        # We'll try to generate a circuit anyway, but it might fail or only satisfy a subset.

    # Create tableau from stabilizers
    try:
        # allow_underconstrained=True because we might have fewer stabilizers than qubits
        # allow_redundant=True because some stabilizers might be dependent
        tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers], allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated successfully.")
        
        # Write to file
        with open(r'data\gemini-3-pro-preview\agent_files\circuit_125.stim', 'w') as f:
            f.write(str(circuit))
        print("Circuit written to file.")
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

def check_commutativity(stabilizers):
    print("Checking commutativity...")
    paulis = [stim.PauliString(s) for s in stabilizers]
    anticommuting_pairs = []
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
    
    if anticommuting_pairs:
        print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
        for i, j in anticommuting_pairs[:10]:
            print(f"Stabilizers {i} and {j} anticommute.")
        return False
    else:
        print("All stabilizers commute.")
        return True

if __name__ == "__main__":
    solve()
