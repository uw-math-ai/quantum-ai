import stim
import sys

def main():
    try:
        with open("stabilizers.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        stabilizers = []
        for line in lines:
            # Handle potential comma separation or just raw strings
            parts = line.split(',')
            stabilizers.append(parts[0].strip())

        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        # Convert to PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Create tableau
        # allow_redundant=True in case user provided dependent generators (though ideal they are independent)
        # allow_underconstrained=True if fewer than 45 independent generators
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        
        # Verify valid stabilizers
        # The prompt asks for a circuit that prepares this state.
        # "elimination" method: Gaussian elimination to find a circuit preparing the state from |0>
        circuit = tableau.to_circuit("elimination")
        
        with open("circuit_attempt.stim", "w") as f:
            f.write(str(circuit))
            
        print("Circuit generated and saved to circuit_attempt.stim")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
