import stim
import sys

def main():
    try:
        with open("baseline_task.stim", "r") as f:
            baseline_text = f.read()
        circuit = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # Tableau from circuit
    tableau = stim.Tableau.from_circuit(circuit)

    # Graph state circuit
    graph_circuit = tableau.to_circuit(method="graph_state")

    # Clean resets
    clean_circuit = stim.Circuit()
    for instruction in graph_circuit:
        if instruction.name == "RX":
            clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name in ["R", "RZ"]:
            # R is Reset Z. Assume already 0.
            pass 
        else:
            clean_circuit.append(instruction)

    # Write
    with open("candidate.stim", "w") as f:
        f.write(str(clean_circuit))

    print("Candidate generated in candidate.stim")

if __name__ == "__main__":
    main()
