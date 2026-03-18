import stim

def run():
    # Load baseline
    circuit = stim.Circuit.from_file("baseline_task.stim")
    
    # Get tableau
    sim = stim.TableauSimulator()
    sim.do(circuit)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize
    candidate = tableau.to_circuit(method="graph_state")
    
    new_circuit = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            for t in instruction.targets_copy():
                new_circuit.append("H", [t])
        else:
            new_circuit.append(instruction)
            
    # Save
    with open("candidate_task.stim", "w") as f:
        f.write(str(new_circuit))
        
    # Check stats
    num_cx = sum(1 for inst in new_circuit if inst.name == "CX")
    num_cz = sum(1 for inst in new_circuit if inst.name == "CZ")
    print(f"Generated candidate with {num_cx} CX and {num_cz} CZ gates.")

if __name__ == "__main__":
    run()