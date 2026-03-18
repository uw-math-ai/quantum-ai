import stim

def main():
    try:
        # Load stabilizers
        with open("target_stabilizers_new.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        # Create Tableau from stabilizers
        # We need to handle the case where the stabilizers are underconstrained or overconstrained
        # The prompt says "Target stabilizers (must all be preserved)".
        # It implies they form a stabilizer group.
        # Let's check the number of qubits.
        num_qubits = len(stabilizers[0])
        print(f"Number of qubits: {num_qubits}")
        print(f"Number of stabilizers: {len(stabilizers)}")

        # Convert strings to PauliStrings
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

        # Create a Tableau from the stabilizers
        try:
            tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
            print("Successfully created Tableau from stabilizers.")
            
            # Synthesize
            circuit_elim = tableau.to_circuit(method="elimination")
            circuit_graph = tableau.to_circuit(method="graph_state")
            
            # Print basic stats
            print(f"Elimination circuit stats: {circuit_elim.num_operations}")
            print(f"Graph state circuit stats: {circuit_graph.num_operations}")

            # decomposed graph state to CX
            # CZ(a,b) = H(b) CX(a,b) H(b)
            # But maybe we can do better.
            
        except Exception as e:
            print(f"Error creating Tableau: {e}")
            import traceback
            traceback.print_exc()
            return

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
