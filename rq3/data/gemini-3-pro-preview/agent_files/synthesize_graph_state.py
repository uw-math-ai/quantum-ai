import stim

def synthesize():
    with open("target_stabilizers_current.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Create tableau from stabilizers
    # Note: from_stabilizers expects a list of stim.PauliString.
    
    pauli_strings = [stim.PauliString(line) for line in lines]
    tableau = stim.Tableau.from_stabilizers(pauli_strings)

    # Synthesize using graph_state method
    circuit = tableau.to_circuit(method="graph_state")

    # Optimization: Replace RX with H (assuming input |0>)
    # Stim's graph state synthesis uses RX to prepare |+> states.
    # Since we start with |0>, H is equivalent to preparing |+>.
    # Also we want to avoid Resets if possible as per instructions (unless required).
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX target is reset to |+>. H on |0> is |+>.
            # We assume the circuit starts with |0>.
            # So replacing RX with H is valid for state prep.
            new_circuit.append("H", instruction.targets_copy())
        else:
            new_circuit.append(instruction)

    print(new_circuit)

if __name__ == "__main__":
    synthesize()
