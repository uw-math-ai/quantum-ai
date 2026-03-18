import stim

def generate_circuit():
    with open("target_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Convert to PauliStrings
    pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]

    # Create Tableau from stabilizers
    t = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
    
    # Synthesize circuit using graph_state method (produces CZ gates)
    circuit = t.to_circuit(method="graph_state")
    
    new_circuit = stim.Circuit()
    
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX with H
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        elif instruction.name in ["R", "RZ"]:
            # Drop resets to |0>
            continue
        elif instruction.name == "TICK":
             continue
        else:
            new_circuit.append(instruction)
            
    # Break down long instructions
    final_lines = []
    for instruction in new_circuit:
        if instruction.name == "CZ" and len(instruction.targets_copy()) > 10:
            print(f"Found large CZ with {len(instruction.targets_copy())} targets")
            targets = instruction.targets_copy()
            # Iterate in pairs
            for i in range(0, len(targets), 2):
                t1 = targets[i]
                t2 = targets[i+1]
                # t1, t2 are GateTarget. 
                # We need the qubit index or proper string representation.
                # Assuming simple qubit targets for graph state.
                final_lines.append(f"CZ {t1.value} {t2.value}")
        else:
            final_lines.append(str(instruction))

    return final_lines

if __name__ == "__main__":
    circuit_lines = generate_circuit()
    # Write to file
    with open("candidate.stim", "w") as f:
        for line in circuit_lines:
            f.write(line + "\n")
    
    print("Generated candidate.stim")
