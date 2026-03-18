import stim
import sys

def main():
    # Read the stabilizers
    with open("target_stabilizers_rq3_new_v3.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(stabilizers)} stabilizers.")
    if len(stabilizers) > 0:
        print(f"Stabilizer length: {len(stabilizers[0])}")

    # Convert to PauliStrings
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    # Create Tableau
    try:
        # allow_underconstrained=True because 152 stabilizers for 153 qubits
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
        print(f"Tableau created. Size: {len(tableau)}")
        
        # Synthesize circuit
        circuit = tableau.to_circuit(method="graph_state")
        print(f"Circuit synthesized. Num qubits: {circuit.num_qubits}")
        
        # Ensure the circuit has the correct number of qubits by adding an Identity gate on the last qubit if needed
        if circuit.num_qubits < 153:
            print("Padding circuit to 153 qubits")
            circuit.append("I", [152])
            
        print(f"Final circuit num_qubits: {circuit.num_qubits}")
        
        # Save candidate
        with open("candidate_rq3_new_v4.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error creating tableau or circuit: {e}")
        return

if __name__ == "__main__":
    main()
