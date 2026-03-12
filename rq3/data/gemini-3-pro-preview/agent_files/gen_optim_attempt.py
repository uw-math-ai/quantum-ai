import stim
import sys

def main():
    try:
        # Read stabilizers
        with open("target_stabs.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        # Create Tableau from stabilizers
        # We need to convert string stabilizers to PauliStrings
        pauli_stabilizers = [stim.PauliString(line) for line in lines]
        
        # Attempt to create a tableau
        # allow_redundant=True is often needed if the stabilizers are not independent
        # allow_underconstrained=True is needed if we have fewer stabilizers than qubits
        tableau = stim.Tableau.from_stabilizers(
            pauli_stabilizers, 
            allow_redundant=True, 
            allow_underconstrained=True
        )
        
        # Synthesize circuit using graph_state method
        circuit = tableau.to_circuit(method="graph_state")
        
        # Check if we need to replace RX with H (if the circuit starts with RX, it might be due to graph state starting basis)
        # Graph state synthesis usually starts with H on all qubits then CZs then local Cliffords.
        # However, stim might output RX for some reason?
        # Actually, stim's graph_state method produces operations like H, S, CZ, SQRT_X etc.
        # But 'RX' gate implies a reset or rotation. Reset is not allowed unless present in baseline.
        # If stim produces RX as a gate (Rotation X? No, Stim's RX is Reset X).
        # We should check if the output contains resets.
        
        print(circuit)
        
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
