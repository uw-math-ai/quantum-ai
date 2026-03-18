import stim
import sys

def main():
    # Read stabilizers
    try:
        with open('target_stabilizers_current.txt', 'r') as f:
            stabilizer_strs = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: target_stabilizers_current.txt not found")
        return

    # Convert to stim.PauliString
    stabilizers = [stim.PauliString(s) for s in stabilizer_strs]

    # Create tableau
    # allow_redundant=True is crucial as some stabilizers might be dependent
    # allow_underconstrained=True allows for fewer stabilizers than qubits
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit using graph state method
    # This usually produces a circuit with H, S, CZ, and single qubit cliffords.
    # It often starts by resetting qubits.
    circuit = tableau.to_circuit(method="graph_state")

    # Post-process to remove resets if we assume start state |0>
    clean_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "R" or instruction.name == "RZ":
            # Reset to 0. Since we start at 0, we can ignore this.
            continue
        elif instruction.name == "RX":
            # Reset to +. Since we start at 0, this is H.
            clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "RY":
             # Reset to i. Since we start at 0, this is H then S.
             clean_circuit.append("H", instruction.targets_copy())
             clean_circuit.append("S", instruction.targets_copy())
        elif instruction.name == "TICK":
            continue
        else:
            clean_circuit.append(instruction)

    # print(clean_circuit)
    with open("candidate_graph.stim", "w") as f:
        f.write(str(clean_circuit))

if __name__ == "__main__":
    main()
