import stim

def convert_cz_to_cx(circuit):
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "CZ":
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                # CZ(c, t) = H(t) CX(c, t) H(t)
                # Note: c and t are stim.GateTarget objects, need their value
                # Assuming simple qubit targets for now.
                new_circuit.append("H", [t])
                new_circuit.append("CX", [c, t])
                new_circuit.append("H", [t])
        else:
            new_circuit.append(instruction)
    return new_circuit

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    for instruction in circuit:
        if instruction.name == "CX":
            n = len(instruction.targets_copy()) // 2
            cx_count += n
            volume += n
        elif instruction.name == "CZ":
             n = len(instruction.targets_copy()) // 2
             # If we treat CZ as 1 gate in volume (it's in the set):
             volume += n
        else:
            volume += len(instruction.targets_copy())
    return cx_count, volume

def main():
    print("Loading baseline...")
    with open("current_task_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
        
    sim = stim.TableauSimulator()
    sim.do_circuit(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    print("Synthesizing graph state...")
    # 'graph_state' method tries to make a circuit with H, S, CZ, CX, etc. but dominated by CZ
    candidate_graph = tableau.to_circuit(method="graph_state")
    
    cx_g, vol_g = count_metrics(candidate_graph)
    print(f"Graph State Metrics: CX={cx_g}, Volume={vol_g}")
    
    print("Converting CZ to CX...")
    candidate_cx = convert_cz_to_cx(candidate_graph)
    
    cx_c, vol_c = count_metrics(candidate_cx)
    print(f"Converted Metrics: CX={cx_c}, Volume={vol_c}")
    
    # Verify stabilizers
    print("Verifying stabilizers...")
    with open("current_task_stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    sim2 = stim.TableauSimulator()
    sim2.do_circuit(candidate_cx)
    preserved = 0
    for s in stabs:
        if sim2.peek_observable_expectation(stim.PauliString(s)) == 1:
            preserved += 1
            
    print(f"Preserved: {preserved}/{len(stabs)}")
    
    if preserved == len(stabs):
        print("Candidate is VALID.")
        with open("candidate.stim", "w") as f:
            f.write(str(candidate_cx))
        print("Written to candidate.stim")
    else:
        print("Candidate is INVALID.")

if __name__ == "__main__":
    main()
