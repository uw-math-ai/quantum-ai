import stim

def generate_circuit():
    with open("target_stabilizers_clean.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Convert to stim.PauliString
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

    # Create tableau
    # Using allow_underconstrained=True because we might not specify the full state
    tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)

    # Synthesize circuit using graph state method
    circuit = tableau.to_circuit(method="graph_state")

    # Replace RX with H for compatibility if needed (assuming input is |0>)
    # Graph state synthesis usually outputs RX(q) which resets q to |+>. 
    # If we start with |0>, H(q) creates |+>.
    # If the circuit assumes initialized qubits, RX is redundant/reset.
    # However, strict replacement: RX is a reset. 
    # If the baseline does NOT have resets, we should probably use H.
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX with H on the same targets
            for target in instruction.targets_copy():
                new_circuit.append("H", [target])
        else:
            new_circuit.append(instruction)

    print(new_circuit)

if __name__ == "__main__":
    generate_circuit()
