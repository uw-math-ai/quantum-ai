import stim

def count_cx_volume(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            n = len(instr.targets_copy()) // 2
            cx_count += n
            volume += n
        elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "CZ"]:
            if instr.name == "CZ":
                n = len(instr.targets_copy()) // 2
                volume += n
            else:
                volume += len(instr.targets_copy())
        
    return cx_count, volume

def decompose_cz_to_cx(circuit):
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                t1 = targets[i]
                t2 = targets[i+1]
                # CZ = H(t2) CX(t1, t2) H(t2)
                # Ensure we handle qubits correctly.
                new_circuit.append("H", [t2])
                new_circuit.append("CX", [t1, t2])
                new_circuit.append("H", [t2])
        else:
            new_circuit.append(instr)
    return new_circuit

def run():
    print("Loading stabilizers...")
    with open("stabilizers_new.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    stim_stabilizers = [stim.PauliString(s) for s in stabilizers]
    
    print("Generating tableau...")
    # Generate tableau
    tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_redundant=True, allow_underconstrained=True)
    
    # Generate graph state circuit 
    print("Synthesizing graph state circuit...")
    circuit_graph = tableau.to_circuit(method="graph_state")
    circuit_graph_cx = decompose_cz_to_cx(circuit_graph)
    cx_graph, vol_graph = count_cx_volume(circuit_graph_cx)
    print(f"Graph State CX: {cx_graph}, Volume: {vol_graph}")

    print("Synthesizing elimination circuit...")
    circuit_elim = tableau.to_circuit(method="elimination")
    cx_elim, vol_elim = count_cx_volume(circuit_elim)
    print(f"Elimination CX: {cx_elim}, Volume: {vol_elim}")
    
    # Select best
    best_cand = None
    if cx_graph < cx_elim:
        best_cand = circuit_graph_cx
        print("Graph state is better.")
    else:
        best_cand = circuit_elim
        print("Elimination is better.")

    # Load baseline
    print("Loading baseline...")
    with open("baseline_new.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    cx_base, vol_base = count_cx_volume(baseline)
    print(f"Baseline CX: {cx_base}, Volume: {vol_base}")

    cx_cand, vol_cand = count_cx_volume(best_cand)
    print(f"Best Candidate CX: {cx_cand}, Volume: {vol_cand}")
    
    if cx_cand < cx_base:
        print("Candidate is better!")
        with open("candidate_new.stim", "w") as f:
            f.write(str(best_cand))
            
        # Verify preservation
        print("Verifying stabilizer preservation...")
        sim = stim.TableauSimulator()
        sim.do(best_cand)
        
        all_preserved = True
        for s_str in stabilizers:
            s = stim.PauliString(s_str)
            expectation = sim.peek_observable_expectation(s)
            if expectation != 1:
                print(f"Stabilizer {s_str} NOT preserved! Expectation: {expectation}")
                all_preserved = False
                break
        
        if all_preserved:
            print("All stabilizers preserved locally.")
        else:
            print("Stabilizer preservation failed!")
            
    else:
        print("Candidate is NOT better in CX count.")

if __name__ == "__main__":
    run()
