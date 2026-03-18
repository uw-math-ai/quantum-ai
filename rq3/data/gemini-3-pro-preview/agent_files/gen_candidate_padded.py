import stim

def main():
    with open('target_stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Pad stabilizers to 175 qubits
    num_qubits = 175
    stabilizers = []
    for line in lines:
        if len(line) < num_qubits:
            padded = line + 'I' * (num_qubits - len(line))
            stabilizers.append(stim.PauliString(padded))
        else:
            stabilizers.append(stim.PauliString(line))
    
    # Generate tableau
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    
    # Synthesize circuit
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process
    final_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            final_circuit.append("H", instruction.targets_copy())
        else:
            final_circuit.append(instruction)
            
    with open('candidate_padded.stim', 'w') as f:
        print(final_circuit, file=f)

    print("Candidate generated with padding.")

if __name__ == "__main__":
    main()
