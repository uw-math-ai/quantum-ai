import stim

def generate_circuit():
    with open("circuit_input.stim", "r") as f:
        circuit_str = f.read()
    
    # Parse circuit string to stim circuit object
    original_circuit = stim.Circuit(circuit_str)
    
    with open("stabilizers_correct.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    # We will append the stabilizer checks to the end of the original circuit
    new_circuit = original_circuit.copy()
    
    # Start assigning ancillas from qubit 35 (since data qubits are 0-34)
    start_ancilla = 35
    current_ancilla = start_ancilla
    
    flag_qubits = []
    
    for stab_str in stabilizers:
        ancilla = current_ancilla
        current_ancilla += 1
        # Count weight
        weight = sum(1 for c in stab_str if c != 'I')
        
        if weight < 4:
            # Simple gadget
            flag_qubits.append(ancilla)
            new_circuit.append("H", [ancilla])
            
            for q_idx, char in enumerate(stab_str):
                if char == 'I':
                    continue
                elif char == 'X':
                    new_circuit.append("CX", [ancilla, q_idx])
                elif char == 'Z':
                    new_circuit.append("CZ", [ancilla, q_idx])
                elif char == 'Y':
                    new_circuit.append("S_DAG", [q_idx])
                    new_circuit.append("CX", [ancilla, q_idx])
                    new_circuit.append("S", [q_idx])
            
            new_circuit.append("H", [ancilla])
            
        else:
            # Flag gadget
            # Need extra ancilla
            flag_ancilla = current_ancilla
            current_ancilla += 1
            
            flag_qubits.append(ancilla)
            flag_qubits.append(flag_ancilla)
            
            new_circuit.append("H", [ancilla])
            new_circuit.append("H", [flag_ancilla])
            
            # CX M F (M control, F target)
            new_circuit.append("CX", [ancilla, flag_ancilla])
            
            # Coupling
            for q_idx, char in enumerate(stab_str):
                if char == 'I':
                    continue
                elif char == 'X':
                    new_circuit.append("CX", [ancilla, q_idx])
                elif char == 'Z':
                    new_circuit.append("CZ", [ancilla, q_idx])
                elif char == 'Y':
                    new_circuit.append("S_DAG", [q_idx])
                    new_circuit.append("CX", [ancilla, q_idx])
                    new_circuit.append("S", [q_idx])

            # CX M F
            new_circuit.append("CX", [ancilla, flag_ancilla])
            
            new_circuit.append("H", [ancilla])
            new_circuit.append("H", [flag_ancilla])
        
        # Measurement is implicit at end
        
    return new_circuit, flag_qubits

def main():
    circuit, flags = generate_circuit()
    
    # Save to file
    with open("candidate.stim", "w") as f:
        f.write(str(circuit))
        
    # Print flags for easy reading
    print("FLAGS:", flags)

if __name__ == "__main__":
    main()
