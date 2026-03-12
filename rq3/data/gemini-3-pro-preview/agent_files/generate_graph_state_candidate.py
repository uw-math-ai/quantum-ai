import stim
import sys

def generate_candidate():
    try:
        # Read stabilizers
        with open("my_target_stabilizers.txt", "r") as f:
            content = f.read()
        
        # Split by comma and strip whitespace
        lines = [part.strip() for part in content.replace('\n', '').split(',') if part.strip()]
        
        if not lines:
            raise ValueError("No stabilizers found")

        # Determine number of qubits from the longest stabilizer
        num_qubits = max(len(line) for line in lines)
        
        # Pad shorter lines with 'I'
        padded_lines = [line.ljust(num_qubits, 'I') for line in lines]
        
        # Create Tableau
        # Note: stim.Tableau.from_stabilizers expects a list of stim.PauliString
        pauli_stabs = [stim.PauliString(s) for s in padded_lines]
        
        tableau = stim.Tableau.from_stabilizers(
            pauli_stabs, 
            allow_redundant=True, 
            allow_underconstrained=True
        )
        
        # Synthesize circuit
        # method="graph_state" usually produces H and CZ gates + local Cliffords
        circuit = tableau.to_circuit(method="graph_state")
        
        # Post-processing to match constraints
        # 1. Replace RX with H (since we start at |0>, RX is effectively H init, but RX is a reset)
        # 2. Keep other gates.
        
        new_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                # Check if it targets all qubits or specific ones
                # Graph state synthesis usually puts RX on all qubits involved in the graph state at the beginning
                new_circuit.append("H", instr.targets_copy())
            else:
                new_circuit.append(instr)
                
        print(new_circuit)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    generate_candidate()
