import stim

def generate_circuit():
    with open("target_stabilizers_rq3_new.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    # Create PauliStrings
    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line: {line}")
            raise e

    # Create Tableau
    # allow_underconstrained=True because we might have fewer stabilizers than qubits (though 161 lines for 161 qubits usually)
    # allow_redundant=True just in case
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize
    # method="graph_state" is usually optimal for CX count (uses CZ)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "R":
            continue
        elif instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "TICK":
            continue
        else:
            new_circuit.append(instruction)

    # Print raw circuit text without wrapping (if possible)
    # Stim's str() wraps. We can manually reconstruct.
    for instruction in new_circuit:
        name = instruction.name
        targets = []
        for t in instruction.targets_copy():
            if t.is_qubit_target:
                targets.append(str(t.value))
            elif t.is_x_target:
                targets.append(f"X{t.value}")
            elif t.is_y_target:
                targets.append(f"Y{t.value}")
            elif t.is_z_target:
                targets.append(f"Z{t.value}")
            elif t.is_combiner:
                targets.append("*")
            else:
                targets.append(str(t)) 
        print(f"{name} {' '.join(targets)}")

if __name__ == "__main__":
    generate_circuit()
