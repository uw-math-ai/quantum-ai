import stim

def prepare_circuit():
    with open("candidate_graph.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "RX":
            # Replace RX with H for all targets
            targets = instr.targets_copy()
            new_circuit.append("H", targets)
        elif instr.name == "TICK":
            continue
        else:
            new_circuit.append(instr)
            
    # Verify strict CX count is 0
    cx_count = 0
    for instr in new_circuit:
        if instr.name in ["CX", "CNOT"]:
            cx_count += len(instr.targets_copy()) // 2
    
    print(f"Candidate CX count: {cx_count}")
    
    # Save
    with open("candidate_formatted.stim", "w") as f:
        f.write(str(new_circuit))

    # Verify stabilizers
    # We need to check if new_circuit applied to |0> stabilizes the targets.
    # Load targets
    with open("current_task_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stim_stabilizers = []
    for line in lines:
        stim_stabilizers.append(stim.PauliString(line))
        
    # Simulate using TableauSimulator
    sim = stim.TableauSimulator()
    sim.do(new_circuit)
    
    print("Verifying stabilizers...")
    all_good = True
    for s in stim_stabilizers:
        res = sim.peek_observable_expectation(s)
        if res != 1:
            print(f"Failed stabilizer: {s} -> expectation {res}")
            all_good = False
            # break  # Continue checking all for debugging
            
    if all_good:
        print("All stabilizers preserved.")
    else:
        print("Stabilizer check failed.")

if __name__ == "__main__":
    prepare_circuit()
