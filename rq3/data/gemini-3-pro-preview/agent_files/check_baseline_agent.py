import stim

def check_baseline(stabilizers_file, baseline_file):
    # Load stabilizers
    with open(stabilizers_file, 'r') as f:
        content = f.read().strip()
    stabilizers = [stim.PauliString(s.strip()) for s in content.replace('\n', '').split(',') if s.strip()]
    
    # Load baseline
    with open(baseline_file, 'r') as f:
        baseline_circuit = stim.Circuit(f.read())
        
    print(f"Loaded {len(stabilizers)} stabilizers.")
    print(f"Loaded baseline with {len(baseline_circuit)} instructions.")
    
    # Simulate baseline
    sim = stim.TableauSimulator()
    sim.do(baseline_circuit)
    
    # Check stabilizers
    all_good = True
    for i, s in enumerate(stabilizers):
        if not sim.peek_observable_expectation(s):
            print(f"Stabilizer {i} NOT preserved: {s}")
            all_good = False
            # Break early if many fail?
            # break
    
    if all_good:
        print("All stabilizers preserved by baseline.")
        
        # Get tableau from simulator
        tableau = sim.current_inverse_tableau().inverse()
        print("Tableau extracted from baseline.")
        return tableau
    else:
        print("Baseline failed to preserve stabilizers.")
        return None

if __name__ == "__main__":
    tableau = check_baseline("agent_stabilizers.txt", "baseline_agent.stim")
    if tableau:
        # Generate circuit from this valid tableau
        circuit = tableau.to_circuit(method='graph_state')
        
        # Replace RX with H if needed
        new_circuit = stim.Circuit()
        for instruction in circuit:
            if instruction.name == "RX":
                new_circuit.append("H", instruction.targets_copy())
            else:
                new_circuit.append(instruction)
                
        with open("agent_candidate.stim", "w") as f:
            f.write(str(new_circuit))
        print("Generated agent_candidate.stim from baseline tableau.")
