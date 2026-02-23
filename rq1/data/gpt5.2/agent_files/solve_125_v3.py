import stim
import sys

def solve():
    print("Reading stabilizers from file...", file=sys.stderr)
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_125_new.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Stabilizer file not found.", file=sys.stderr)
        return

    stabilizers = [stim.PauliString(s) for s in lines]
    print(f"Loaded {len(stabilizers)} stabilizers.", file=sys.stderr)
    n_qubits = len(stabilizers[0])
    print(f"Number of qubits: {n_qubits}", file=sys.stderr)

    # Check for anticommuting pairs
    print("Checking commutativity...", file=sys.stderr)
    anticommuting = False
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                # print(f"Stabilizers {i} and {j} anticommute.", file=sys.stderr)
                anticommuting = True
                # break
    
    if anticommuting:
        print("WARNING: Anticommuting pairs found!", file=sys.stderr)
    else:
        print("All stabilizers commute.", file=sys.stderr)

    try:
        # Create tableau from stabilizers
        # If they anticommute, this might fail or produce a state that doesn't satisfy all.
        # But we'll try.
        tableau = stim.Tableau.from_stabilizers(
            stabilizers, 
            allow_underconstrained=True, 
            allow_redundant=True
        )
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated successfully.", file=sys.stderr)
        
        # Print ONLY the circuit to stdout
        print(circuit)
            
    except Exception as e:
        print(f"Error generating circuit: {e}", file=sys.stderr)

if __name__ == "__main__":
    solve()
