import stim

baseline_file = "baseline_prompt.stim"
output_file = "candidate_prompt.stim"

print(f"Reading baseline from {baseline_file}...")
with open(baseline_file, "r") as f:
    baseline_str = f.read()

try:
    baseline = stim.Circuit(baseline_str)
    
    print("Simulating baseline to get tableau...")
    sim = stim.TableauSimulator()
    sim.do(baseline)
    # Extract the stabilizer tableau corresponding to the state
    tableau = sim.current_inverse_tableau().inverse()
    
    print("Synthesizing graph state circuit...")
    # method="graph_state" uses H, S, CZ, SQRT_X
    candidate = tableau.to_circuit(method="graph_state")
    
    # Post-process to remove resets (R) and split long instructions
    final_circuit = stim.Circuit()
    
    for instruction in candidate:
        name = instruction.name
        targets = instruction.targets_copy()
        
        # Handle resets by replacing with gates acting on |0>
        if name == "RX":
            # RX resets to |0> then applies X, effectively preparing |+> from |0>? 
            # No, RX is "Reset X". It measures X and forces it to +1 (eigenstate |+>).
            # If we start from |0>, to get |+>, we just apply H.
            # So RX -> H.
            for t in targets:
                final_circuit.append("H", [t])
        elif name == "RY":
            # RY is Reset Y -> |+i>. From |0>, H then S gives |+i>.
            for t in targets:
                final_circuit.append("H", [t])
                final_circuit.append("S", [t])
        elif name == "RZ" or name == "R":
            # RZ is Reset Z -> |0>. If we are already at |0> (or effectively handled by previous ops), we can skip.
            # However, graph state synthesis puts resets at the beginning to clear the state.
            # Since our baseline assumes |0> input, we can just skip these.
            pass
        elif name == "CZ":
             # Split CZ into pairs
             for i in range(0, len(targets), 2):
                 final_circuit.append("CZ", targets[i:i+2])
        else:
             # Split other gates into reasonable chunks (e.g. 10) to avoid huge lines
             chunk_size = 10
             for i in range(0, len(targets), chunk_size):
                 final_circuit.append(name, targets[i:i+chunk_size])
        
    # Write to file manually to ensure splitting
    with open(output_file, "w") as f:
        for instruction in final_circuit:
            name = instruction.name
            if name == "CZ":
                 # Write as pairs
                 targets = instruction.targets_copy()
                 for i in range(0, len(targets), 2):
                     f.write(f"CZ {targets[i].value} {targets[i+1].value}\n")
            elif name in ["H", "X", "Y", "Z", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]:
                 # Split single qubit gates for readability too
                 targets = instruction.targets_copy()
                 for t in targets:
                     f.write(f"{name} {t.value}\n")
            elif name == "TICK":
                 # skip ticks or write them
                 pass 
            else:
                 f.write(str(instruction) + "\n")

    print(f"Generated {output_file}.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
