
import stim
import sys

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX":
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    # Volume is total gate count in volume gate set
    vol = 0
    for op in circuit:
        if op.name in ["CX", "CY", "CZ"]:
            vol += len(op.targets_copy()) // 2
        elif op.name in ["H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            vol += len(op.targets_copy())
    return vol

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    stabilizers = []
    for line in lines:
        line = line.replace(',', '')
        stabilizers.append(stim.PauliString(line))
    return stabilizers

def verify_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    for stab in stabilizers:
        if sim.peek_observable_expectation(stab) != 1:
            return False
    return True

def convert_cz_to_cx(circuit):
    new_circuit = stim.Circuit()
    for op in circuit:
        if op.name == "CZ":
            targets = op.targets_copy()
            for i in range(0, len(targets), 2):
                t1 = targets[i]
                t2 = targets[i+1]
                # CZ 0 1 = H 1 CX 0 1 H 1
                new_circuit.append("H", [t2])
                new_circuit.append("CX", [t1, t2])
                new_circuit.append("H", [t2])
        else:
            new_circuit.append(op)
    return new_circuit

def main():
    print("Reading baseline...")
    with open("baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    base_cx = count_cx(baseline)
    base_vol = count_volume(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    stabilizers = load_stabilizers("stabilizers.txt")
    
    # Method 1: Elimination
    print("Trying elimination synthesis...")
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
    circ_elim = tableau.to_circuit(method="elimination")
    
    cx_elim = count_cx(circ_elim)
    vol_elim = count_volume(circ_elim)
    print(f"Elimination: CX={cx_elim}, Vol={vol_elim}")
    
    # Method 2: Graph State
    print("Trying graph state synthesis...")
    circ_graph = tableau.to_circuit(method="graph_state")
    
    # Convert CZ to CX
    circ_graph_cx = convert_cz_to_cx(circ_graph)
    
    cx_graph = count_cx(circ_graph_cx)
    vol_graph = count_volume(circ_graph_cx)
    print(f"Graph State (Converted): CX={cx_graph}, Vol={vol_graph}")
    
    # Check if Elimination is better than Baseline
    elim_is_better = False
    if cx_elim < base_cx:
        elim_is_better = True
    elif cx_elim == base_cx and vol_elim < base_vol:
        elim_is_better = True
        
    # Check if Graph is better than Baseline
    graph_is_better = False
    if cx_graph < base_cx:
        graph_is_better = True
    elif cx_graph == base_cx and vol_graph < base_vol:
        graph_is_better = True
        
    print(f"Elimination better? {elim_is_better}")
    print(f"Graph better? {graph_is_better}")
    
    best_circuit = None
    
    if elim_is_better and graph_is_better:
        # Pick the one that is better between them
        if cx_graph < cx_elim:
            best_circuit = circ_graph_cx
            print("Graph wins")
        elif cx_graph == cx_elim and vol_graph < vol_elim:
             best_circuit = circ_graph_cx
             print("Graph wins")
        else:
             best_circuit = circ_elim
             print("Elim wins")
    elif elim_is_better:
        best_circuit = circ_elim
        print("Elim wins")
    elif graph_is_better:
        best_circuit = circ_graph_cx
        print("Graph wins")
    
    if best_circuit:
        with open("candidate.stim", "w") as f:
            f.write(str(best_circuit))
        print("Saved best candidate.")
    else:
        print("No improvement.")
        
    with open("candidate_elim.stim", "w") as f:
        f.write(str(circ_elim))
    
    with open("candidate_graph_converted.stim", "w") as f:
        f.write(str(circ_graph_cx))

if __name__ == "__main__":
    main()
