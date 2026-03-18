import stim

def generate_from_baseline():
    with open("baseline_task.stim", "r") as f:
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    
    # Simulate to get the tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    # Get the state tableau
    t = sim.current_inverse_tableau().inverse()
    
    # Synthesize using graph_state method
    circuit = t.to_circuit(method="graph_state")

    # Post-process to replace RX with H and remove RZ/MY
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "RZ":
            pass # Remove RZ (reset to 0), assuming input is |0>
        elif instruction.name == "MY":
             # Should not happen for standard graph states but if it does, it's a reset.
             new_circuit.append(instruction)
        else:
            new_circuit.append(instruction)
    
    return new_circuit

if __name__ == "__main__":
    c = generate_from_baseline()
    with open("candidate.stim", "w") as f:
        f.write(str(c))
