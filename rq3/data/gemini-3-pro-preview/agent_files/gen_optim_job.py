import stim

def generate_circuit():
    with open("target_stabilizers_new_task.txt", "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    stabilizers = []
    for line in lines:
        # Remove commas if present
        clean_line = line.replace(",", "")
        stabilizers.append(stim.PauliString(clean_line))

    # Create tableau
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Convert to circuit using graph state method
    circuit = tableau.to_circuit(method="graph_state")

    # Post-process to remove resets if they are not allowed/needed
    # We replace RX with H, assuming input is |0>
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX targets
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        else:
            new_circuit.append(instruction)

    print(new_circuit)

if __name__ == "__main__":
    generate_circuit()
