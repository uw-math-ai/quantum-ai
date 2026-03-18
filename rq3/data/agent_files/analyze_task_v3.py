import stim

def count_gates(circuit):
    cx_count = 0
    volume = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            n = len(instruction.targets_copy()) // 2
            cx_count += n
            volume += n
        elif instruction.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I"]:
             volume += len(instruction.targets_copy())
        elif instruction.name in ["M", "R", "RX", "RY", "RZ", "MX", "MY", "MZ", "MPP"]:
             volume += len(instruction.targets_copy())
    return cx_count, volume

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    preserved = 0
    for s in stabilizers:
        if sim.peek_observable_expectation(stim.PauliString(s)) == 1:
            preserved += 1
    return preserved

def main():
    print("Running analyze_task_v3.py")
    
    # Load baseline
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    base_cx, base_vol = count_gates(baseline)
    print(f"Baseline CX: {base_cx}")
    print(f"Baseline Volume: {base_vol}")
    print(f"Baseline Qubits: {baseline.num_qubits}")

    # Load stabilizers
    stabilizers = []
    with open("target_stabilizers.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(line)
    
    print(f"Num stabilizers: {len(stabilizers)}")
    if stabilizers:
        print(f"Stabilizer length: {len(stabilizers[0])}")

    # Check baseline preservation
    preserved = check_stabilizers(baseline, stabilizers)
    print(f"Baseline preserves: {preserved}/{len(stabilizers)}")
    
    if preserved != len(stabilizers):
        print("WARNING: Baseline does not preserve all stabilizers!")

    # Try synthesis
    try:
        paulis = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        
        # Method 1: Graph State
        print("\n--- Method 1: Graph State ---")
        synth_graph = tableau.to_circuit("graph_state")
        syn_cx, syn_vol = count_gates(synth_graph)
        syn_cz = 0
        for instr in synth_graph:
            if instr.name == "CZ":
                syn_cz += len(instr.targets_copy()) // 2
        
        print(f"Synthesized (graph_state) CX: {syn_cx}")
        print(f"Synthesized (graph_state) CZ: {syn_cz}")
        print(f"Synthesized (graph_state) Volume: {syn_vol}")
        
        pres_graph = check_stabilizers(synth_graph, stabilizers)
        print(f"Synthesized (graph_state) preserves: {pres_graph}/{len(stabilizers)}")

        # Method 3: Elimination
        print("\n--- Method 2: Elimination ---")
        synth_elim = tableau.to_circuit("elimination")
        syn_cx3, syn_vol3 = count_gates(synth_elim)
        print(f"Synthesized (elimination) CX: {syn_cx3}")
        print(f"Synthesized (elimination) Volume: {syn_vol3}")
        
        pres_elim = check_stabilizers(synth_elim, stabilizers)
        print(f"Synthesized (elimination) preserves: {pres_elim}/{len(stabilizers)}")
        
        # Create a candidate file from graph state
        # I'll save the graph state circuit to candidate.stim
        with open("candidate_graph.stim", "w") as f:
            f.write(str(synth_graph))

        # Create a candidate converted to CX
        # Convert CZ to CX: CZ a b -> H b CX a b H b
        # But wait, Stim doesn't have a simple "decompose" method for circuits in Python API directly like that?
        # I can write a simple converter.
        
        candidate_cx = stim.Circuit()
        for instr in synth_graph:
            if instr.name == "CZ":
                targets = instr.targets_copy()
                for i in range(0, len(targets), 2):
                    t1 = targets[i]
                    t2 = targets[i+1]
                    # H t2
                    candidate_cx.append("H", [t2])
                    # CX t1 t2
                    candidate_cx.append("CX", [t1, t2])
                    # H t2
                    candidate_cx.append("H", [t2])
            else:
                candidate_cx.append(instr)
        
        cx_count_cx, vol_cx = count_gates(candidate_cx)
        print(f"\n--- Converted Graph State to CX ---")
        print(f"Converted CX: {cx_count_cx}")
        print(f"Converted Volume: {vol_cx}")
        with open("candidate_cx.stim", "w") as f:
            f.write(str(candidate_cx))

    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    main()
