import stim

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            t = instr.targets_copy()
            cx_count += len(t) // 2
            volume += len(t) // 2
        elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "CZ", "SQRT_X", "SQRT_Y", "SQRT_Z"]:
             t = instr.targets_copy()
             volume += len(t)
    return cx_count, volume

def main():
    with open("baseline_task_final.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    cx, vol = count_metrics(baseline)
    print(f"Baseline: CX={cx}, Vol={vol}")

    with open("stabilizers_task_final.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    print(f"Stabilizers: {len(stabs)}")
    
    # Verify baseline preserves them
    sim = stim.TableauSimulator()
    sim.do_circuit(baseline)
    valid = True
    for s in stabs:
        if sim.peek_observable_expectation(stim.PauliString(s)) != 1:
            valid = False
            break
    print(f"Baseline valid: {valid}")

    # Try synthesis
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabs], allow_underconstrained=True)
    
    # Method 1: standard synthesis (Gaussian elimination)
    circ1 = tableau.to_circuit(method="elimination")
    cx1, vol1 = count_metrics(circ1)
    print(f"Elimination: CX={cx1}, Vol={vol1}")
    
    # Method 2: Graph state synthesis (usually much better for stabilizers)
    # Stim doesn't have a direct "to_graph_state_circuit" method exposed nicely via Tableau,
    # but let's check if 'graph_state' is a valid method for to_circuit.
    try:
        circ2 = tableau.to_circuit(method="graph_state")
        
        # Replace RX with H (since we assume |0> input and resets are banned)
        circ2_clean = stim.Circuit()
        for instr in circ2:
            if instr.name == "RX":
                circ2_clean.append("H", instr.targets_copy())
            else:
                circ2_clean.append(instr)
        circ2 = circ2_clean
        
        cx2, vol2 = count_metrics(circ2)
        print(f"GraphState: CX={cx2}, Vol={vol2}")
        
        # Verify it
        sim2 = stim.TableauSimulator()
        sim2.do_circuit(circ2)
        valid2 = True
        for s in stabs:
            if sim2.peek_observable_expectation(stim.PauliString(s)) != 1:
                valid2 = False
                break
        print(f"GraphState valid: {valid2}")
        
        # Save graph state circuit if better
        if valid2 and (cx2 < cx or (cx2 == cx and vol2 < vol)):
            print("Graph state is better!")
            with open("candidate_graph.stim", "w") as f:
                f.write(str(circ2))
                
    except Exception as e:
        print(f"GraphState method failed: {e}")

if __name__ == "__main__":
    main()
