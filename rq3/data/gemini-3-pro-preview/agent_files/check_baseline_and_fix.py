import stim

def main():
    # Read baseline
    with open("baseline_task.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    # Read stabilizers
    with open("target_stabilizers_task.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    stabilizers = [stim.PauliString(l) for l in lines]
    
    # Simulate
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    # Check stabilizers
    results = []
    for i, s in enumerate(stabilizers):
        try:
            exp = sim.peek_observable_expectation(s)
            results.append(exp)
            if exp != 1:
                print(f"Stabilizer {i}: expectation {exp}")
        except Exception as e:
             print(f"Stabilizer {i}: Error checking expectation: {e}")

    # Count
    count_1 = results.count(1)
    count_minus_1 = results.count(-1)
    count_0 = results.count(0)
    
    print(f"Results: +1: {count_1}, -1: {count_minus_1}, 0: {count_0}")
    
    # If all are +1 or -1, we can create a Tableau from the correct signs.
    if count_0 == 0:
        new_stabilizers = []
        for i, s in enumerate(stabilizers):
            if results[i] == 1:
                new_stabilizers.append(s)
            elif results[i] == -1:
                new_stabilizers.append(s * -1) # Add negative sign
        
        # Try creating Tableau again with corrected signs
        try:
            tableau = stim.Tableau.from_stabilizers(new_stabilizers, allow_underconstrained=True, allow_redundant=True)
            print("Successfully created Tableau with corrected signs!")
            
            # Synthesize
            circuit = tableau.to_circuit(method="graph_state")
            
            # Post process
            new_circuit = stim.Circuit()
            for instruction in circuit:
                if instruction.name == "RX":
                    new_circuit.append("H", instruction.targets_copy())
                elif instruction.name in ["R", "RZ"]:
                    pass
                else:
                    new_circuit.append(instruction)
            
            out_file = "candidate_graph_state_corrected.stim"
            with open(out_file, "w") as f:
                f.write(str(new_circuit))
            print(f"Written corrected candidate to {out_file}")
            
        except Exception as e:
            print(f"Error creating tableau with corrected signs: {e}")

if __name__ == "__main__":
    main()
