import stim

def check_stabilizers_preserved(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for s in stabilizers:
        if sim.peek_observable_expectation(s) != 1:
            return False
    return True

def count_metrics(circuit):
    num_cx = 0
    num_volume = 0
    for instr in circuit:
        if instr.name == "CX":
            num_cx += len(instr.targets_copy()) // 2
        elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "CZ", "CY", "XCZ", "YCX"]:
            num_volume += len(instr.targets_copy())
            if instr.name in ["CZ", "CY", "XCZ", "YCX"]: 
                 num_volume += len(instr.targets_copy()) // 2 
    return num_cx, num_volume

def load_stabilizers(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    stabilizers = [stim.PauliString(line.strip()) for line in lines if line.strip()]
    return stabilizers

def convert_graph_to_cx(circuit):
    # Heuristic: Convert CZ(a, b) to CX(a, b) H(b) or CX(b, a) H(a)
    # But graph state is H + CZ.
    # We want to minimize CX. 1 CZ = 1 CX + 2 H.
    # The CX count is the number of CZ gates.
    # Volume will be higher because of H.
    # But if baseline has 266 CX, and graph state has fewer edges, we win on CX.
    # If edges = 266, we likely lose on volume.
    
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                a = targets[i]
                b = targets[i+1]
                # Convert CZ(a, b) -> H(b) CX(a, b) H(b)
                new_circuit.append("H", [b])
                new_circuit.append("CX", [a, b])
                new_circuit.append("H", [b])
        else:
            new_circuit.append(instr)
    return new_circuit

def main():
    try:
        stabilizers = load_stabilizers("current_task_stabilizers.txt")
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        with open("current_task_baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        base_cx, base_vol = count_metrics(baseline)
        print(f"Baseline: CX={base_cx}, Volume={base_vol}, Instructions={len(baseline)}")
        
        if check_stabilizers_preserved(baseline, stabilizers):
            print("Baseline is VALID.")
        else:
            print("Baseline is INVALID.")
            
        # Strategy 1: Elimination
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circ_elim = tableau.to_circuit(method="elimination")
        elim_cx, elim_vol = count_metrics(circ_elim)
        print(f"Elimination: CX={elim_cx}, Volume={elim_vol}")
        
        # Strategy 2: Graph State
        circ_graph = tableau.to_circuit(method="graph_state")
        # Graph state circuit uses H, S, CZ, etc.
        # We need to convert it to standard gates to count 'cx_count' correctly if evaluating with our tool?
        # No, evaluate_optimization counts "cx_count". CZ is not CX.
        # Wait, the definition says:
        # a. cx_count – number of CX (CNOT) gates.
        # b. volume – total gate count in the volume gate set (CX, CY, CZ, H, S, ...).
        # So CZ contributes to volume but not CX count? 
        # If so, a graph state circuit with 0 CX and N CZ gates would have cx_count=0!
        # THIS IS HUGE.
        # But wait, usually physical implementation requires decomposition to CX.
        # If the metric strictly counts "CX" instructions, then CZ gates are free in CX count?
        # If so, graph state is the winner!
        # Let's verify the metric definition in `evaluate_optimization`:
        # "cx_count – number of CX (CNOT) gates (primary, most important)."
        # "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)."
        # It does NOT say "two qubit gate count". It says "CX gate count".
        # This implies CZ gates do not count towards CX count.
        # But standard Stim circuits often assume CZ is available.
        # However, the user might be using a backend that only supports CX.
        # If I submit a circuit with CZ, does it count as 0 CX?
        # If the tool validates with Stim, Stim supports CZ.
        # If I submit CZ, I might get cx_count=0.
        # BUT, usually "cx_count" implies "two-qubit gate count decomposed to CNOTs".
        # If the tool is literal, CZ is 0.
        # I should probably assume the metric implies standard CNOT count.
        # If I submit CZ, the tool might accept it and give me 0 CX count.
        # OR it might reject CZ if it expects only CX.
        # The prompt says "generate a valid Stim circuit". Stim supports CZ.
        # The prompt doesn't say "only use CX".
        # But if the metric is lexicographic (cx_count, volume), and I use CZ...
        # If CZ counts as 0 CX, then graph state is optimal.
        # Let's double check if I should decompose.
        # "optimize this while preserving stabilizers"
        # The baseline uses CX.
        # Usually, comparisons are done on decomposed circuits.
        # If I convert CZ to CX, I get 1 CX per CZ.
        # Let's compare "Elimination" (uses CX) and "Graph State" (uses CZ).
        
        # If I convert Graph State to CX:
        circ_graph_cx = convert_graph_to_cx(circ_graph)
        graph_cx, graph_vol = count_metrics(circ_graph_cx)
        print(f"Graph State (converted to CX): CX={graph_cx}, Volume={graph_vol}")

        # Save the best candidate
        # I'll save both elim and graph_converted.
        with open("candidate_elim.stim", "w") as f:
            f.write(str(circ_elim))
            
        with open("candidate_graph_cx.stim", "w") as f:
            f.write(str(circ_graph_cx))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
