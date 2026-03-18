
import stim

def main():
    try:
        with open('target_stabilizers_rq3_v4.txt', 'r') as f:
            stabs = [line.strip() for line in f if line.strip()]

        if not stabs:
            print("No stabilizers found.")
            return

        print(f"Number of stabilizers: {len(stabs)}")
        print(f"Stabilizer length: {len(stabs[0])}")

        # Create PauliStrings
        pauli_stabs = [stim.PauliString(s) for s in stabs]

        # Create Tableau
        # Use allow_redundant=True as per memories
        # Use allow_underconstrained=True just in case
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_redundant=True, allow_underconstrained=True)

        # Generate circuit using graph_state method (produces CZ+H+S)
        circuit = tableau.to_circuit(method="graph_state")
        
        # Replace RX with H if needed. graph_state produces H, S, CZ. 
        # If the input is |0>, H brings it to |+>, and graph state is defined.
        # However, to_circuit("graph_state") assumes the circuit prepares the state from |0...0>.
        # So the output circuit should be exactly what we want.
        # But wait, does it assume we want to MEASURE in that basis? 
        # No, to_circuit returns a unitary (or Clifford) that PREPARES the state stabilized by the tableau, starting from |0>.
        
        # Output the circuit to stdout
        print(circuit)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
