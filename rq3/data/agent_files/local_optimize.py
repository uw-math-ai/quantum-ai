import stim
import sys

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX":
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for op in circuit:
        if op.name in ["QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "SHIFT_COORDS", "TICK"]:
            continue
        targets = op.targets_copy()
        if op.name in ["CX", "CY", "CZ", "SWAP"]:
            count += len(targets) // 2
        else:
            count += len(targets)
    return count

def get_stabilizers():
    with open("stabilizers.txt", "r") as f:
        lines = [l.strip().replace(',', '') for l in f.read().splitlines() if l.strip()]
    return [stim.PauliString(l) for l in lines]

def solve():
    try:
        stabilizers = get_stabilizers()
        
        with open("baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        
        base_cx = count_cx(baseline)
        base_vol = count_volume(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")

        # Attempt 1: Direct synthesis
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="elimination")
        
        cand_cx = count_cx(circuit)
        cand_vol = count_volume(circuit)
        print(f"Candidate 1 (Elimination): CX={cand_cx}, Vol={cand_vol}")
        
        # Check against baseline
        if cand_cx < base_cx or (cand_cx == base_cx and cand_vol < base_vol):
            print("Candidate 1 is better.")
            with open("best_candidate.stim", "w") as f:
                f.write(str(circuit))
        
        # Attempt 2: Graph state synthesis
        circuit_graph = tableau.to_circuit(method="graph_state")
        cand2_cx = count_cx(circuit_graph)
        cand2_vol = count_volume(circuit_graph)
        print(f"Candidate 2 (Graph State): CX={cand2_cx}, Vol={cand2_vol}")

        if cand2_cx < base_cx or (cand2_cx == base_cx and cand2_vol < base_vol):
            # Check if it's better than candidate 1
            if cand2_cx < cand_cx or (cand2_cx == cand_cx and cand2_vol < cand_vol):
                print("Candidate 2 is better than Candidate 1 and Baseline.")
                with open("best_candidate.stim", "w") as f:
                    f.write(str(circuit_graph))
            elif not (cand_cx < base_cx or (cand_cx == base_cx and cand_vol < base_vol)):
                 # Candidate 1 wasn't better, but Candidate 2 is better than baseline
                 print("Candidate 2 is better than Baseline (Cand 1 was not).")
                 with open("best_candidate.stim", "w") as f:
                    f.write(str(circuit_graph))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
