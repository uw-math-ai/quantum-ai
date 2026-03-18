import stim

def generate_circuit():
    with open("baseline_v2.stim", "r") as f:
        baseline_text = f.read()
    
    # Load baseline
    circuit = stim.Circuit(baseline_text)
    
    # Simulate to get tableau
    sim = stim.TableauSimulator()
    sim.do(circuit)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize using graph_state method
    generated_circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process: Replace RX with H
    new_circuit = stim.Circuit()
    for instruction in generated_circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "R" or instruction.name == "RZ":
            pass # Remove Reset Z
        elif instruction.name == "RY":
             new_circuit.append("H", instruction.targets_copy())
             new_circuit.append("S", instruction.targets_copy())
        else:
            new_circuit.append(instruction)
            
    return new_circuit

if __name__ == "__main__":
    circuit = generate_circuit()
    with open("candidate_graph.stim", "w") as f:
        f.write(str(circuit))
    print("Generated candidate_graph.stim")
