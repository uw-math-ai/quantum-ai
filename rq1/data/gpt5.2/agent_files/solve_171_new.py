import stim
import sys

def solve():
    try:
        # Read stabilizers
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_171_new.txt', 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]

        # Convert to Stim PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

        # Create tableau
        tableau = stim.Tableau.from_stabilizers(
            pauli_stabilizers, 
            allow_underconstrained=True, 
            allow_redundant=True
        )
        
        # Convert to circuit
        circuit = tableau.to_circuit(method='elimination')
        
        # Write circuit to file
        with open("circuit_171.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated successfully to circuit_171.stim")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    solve()
