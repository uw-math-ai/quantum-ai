import stim

def generate_from_baseline(baseline_file):
    with open(baseline_file, 'r') as f:
        baseline = stim.Circuit(f.read())
        
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize using graph state method
    circuit = tableau.to_circuit(method='graph_state')
    
    # Fix RX
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            new_circuit.append("H", instruction.targets_copy())
        else:
            new_circuit.append(instruction)
            
    return new_circuit

if __name__ == "__main__":
    circuit = generate_from_baseline("baseline_agent.stim")
    with open("candidate_agent.stim", "w") as f:
        f.write(str(circuit))
    print("Generated candidate_agent.stim")
