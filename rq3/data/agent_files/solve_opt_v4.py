import stim
import sys

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    
    # Iterate over instructions
    for instruction in circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        
        # Check if it's a gate
        if name in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
            continue
            
        n_targets = len(targets)
        
        # CX count
        if name == "CX" or name == "CNOT":
            gates = n_targets // 2
            cx_count += gates
            volume += gates
        elif name == "CZ":
             gates = n_targets // 2
             volume += gates
        elif name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "I"]:
            volume += n_targets
        elif name in ["SWAP"]:
            gates = n_targets // 2
            volume += gates
            cx_count += 3 * gates
        else:
            if n_targets > 1 and n_targets % 2 == 0:
                 volume += n_targets // 2
            else:
                 volume += n_targets

    return cx_count, volume

def decompose_cz_to_cx(circuit):
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "CZ":
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                t1 = targets[i]
                t2 = targets[i+1]
                new_circuit.append("H", [t2])
                new_circuit.append("CX", [t1, t2])
                new_circuit.append("H", [t2])
        else:
            new_circuit.append(instruction)
    return new_circuit

def main():
    try:
        with open("data/agent_files/baseline.stim", "r") as f:
            baseline_text = f.read()
            baseline = stim.Circuit(baseline_text)
            base_cx, base_vol = count_metrics(baseline)
            print(f"Baseline: CX={base_cx}, Volume={base_vol}")
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # Create tableau from baseline circuit
    try:
        tableau = stim.Tableau.from_circuit(baseline)
    except Exception as e:
        print(f"Error creating tableau from baseline: {e}")
        return

    candidates = []

    # Synthesize using elimination
    try:
        cand_elim = tableau.to_circuit(method="elimination")
        cx_elim, vol_elim = count_metrics(cand_elim)
        print(f"Elimination: CX={cx_elim}, Volume={vol_elim}")
        candidates.append(("Elimination", cand_elim, cx_elim, vol_elim))
    except Exception as e:
        print(f"Elimination failed: {e}")

    # Synthesize using graph_state
    try:
        cand_graph = tableau.to_circuit(method="graph_state")
        cx_graph, vol_graph = count_metrics(cand_graph)
        print(f"Graph State (Raw): CX={cx_graph}, Volume={vol_graph}")
        candidates.append(("Graph Raw", cand_graph, cx_graph, vol_graph))

        # Decomposed
        cand_graph_cx = decompose_cz_to_cx(cand_graph)
        cx_graph_cx, vol_graph_cx = count_metrics(cand_graph_cx)
        print(f"Graph State (Decomposed): CX={cx_graph_cx}, Volume={vol_graph_cx}")
        candidates.append(("Graph Decomposed", cand_graph_cx, cx_graph_cx, vol_graph_cx))
        
    except Exception as e:
        print(f"Graph state failed: {e}")

    best_cand = None
    best_cx = base_cx
    best_vol = base_vol
    best_name = "None"
    
    for name, circ, cx, vol in candidates:
        is_better = False
        if cx < best_cx:
            is_better = True
        elif cx == best_cx and vol < best_vol:
            is_better = True
            
        if is_better:
            print(f"Found better: {name} (CX={cx}, Vol={vol})")
            best_cx = cx
            best_vol = vol
            best_cand = circ
            best_name = name
    
    if best_cand:
        print(f"Writing best candidate ({best_name}) to data/agent_files/candidate.stim")
        with open("data/agent_files/candidate.stim", "w") as f:
            f.write(str(best_cand))
    else:
        print("No strictly better candidate found.")

if __name__ == "__main__":
    main()
