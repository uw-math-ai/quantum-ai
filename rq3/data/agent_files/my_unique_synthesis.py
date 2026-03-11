import stim
import sys

def main():
    try:
        with open('my_prompt_baseline.stim', 'r') as f:
            baseline_text = f.read()
        circuit = stim.Circuit(baseline_text)
    except FileNotFoundError:
        print("Error: my_prompt_baseline.stim not found")
        return

    # Create tableau from circuit (guaranteed to be valid stabilizers for the state prepared by circuit)
    tableau = stim.Tableau.from_circuit(circuit)

    # Synthesize circuit using graph state method
    new_circuit = tableau.to_circuit(method="graph_state")

    # Post-process to remove resets
    clean_circuit = stim.Circuit()
    for instruction in new_circuit:
        if instruction.name == "R" or instruction.name == "RZ":
            pass
        elif instruction.name == "RX":
            clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "RY":
             clean_circuit.append("H", instruction.targets_copy())
             clean_circuit.append("S", instruction.targets_copy())
        elif instruction.name == "TICK":
            pass
        else:
            clean_circuit.append(instruction)

    with open("candidate_final.stim", "w") as f:
        f.write(str(clean_circuit))
    print("Written to candidate_final.stim")

if __name__ == "__main__":
    main()
