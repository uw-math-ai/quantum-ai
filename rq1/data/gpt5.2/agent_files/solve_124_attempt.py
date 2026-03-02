import stim
import sys

def solve():
    try:
        with open("data/stabilizers_124.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = [stim.PauliString(s) for s in lines]
        
        # We have 124 qubits.
        # The stabilizers provided might not be full rank or might be overconstrained.
        # But for 124 qubits, allow_underconstrained=True is key.
        
        tableau = stim.Tableau.from_stabilizers(
            stabilizers,
            allow_redundant=True,
            allow_underconstrained=True
        )
        
        circuit = tableau.to_circuit("elimination")
        
        # Save to file
        with open("circuit_124_attempt.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    solve()
