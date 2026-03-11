import stim

def synthesize_from_baseline():
    # Load baseline
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    
    # Compute tableau
    tableau = stim.Tableau.from_circuit(baseline)
    
    # Synthesize using graph_state
    new_circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process
    clean_circuit = stim.Circuit()
    for instruction in new_circuit:
        if instruction.name == "RX":
            clean_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "RY":
             # RY is Reset Y. +Y state. H then S.
             clean_circuit.append("H", instruction.targets_copy())
             clean_circuit.append("S", instruction.targets_copy())
        elif instruction.name == "RZ":
            pass
        elif instruction.name == "MY":
             # Measurement Y? Graph state synthesis shouldn't produce measurements unless tableau has measurements?
             # But just in case.
             clean_circuit.append(instruction)
        else:
            clean_circuit.append(instruction)

    with open("candidate.stim", "w") as f:
        f.write(str(clean_circuit))

if __name__ == "__main__":
    synthesize_from_baseline()
