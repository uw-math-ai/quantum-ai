import stim

def generate_circuit():
    with open("target_stabilizers_task.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Create tableau from stabilizers
    # Note: from_stabilizers expects a list of PauliString
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])

    # Synthesize using graph_state method
    circuit = t.to_circuit(method="graph_state")

    # Post-process to replace RX with H and remove RZ
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "RZ":
            pass # Remove RZ (reset to 0)
        elif instruction.name == "MY":
             # This is unusual for graph state, but if it appears, it's a reset.
             # Better to fail or handle if we see it.
             # Assuming standard graph state output (RX, CZ, H, S, etc.)
             new_circuit.append(instruction)
        else:
            new_circuit.append(instruction)
    
    return new_circuit

if __name__ == "__main__":
    c = generate_circuit()
    print(c)
