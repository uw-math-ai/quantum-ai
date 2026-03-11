import stim
import sys
import os

STABILIZERS_FILE = r"data\gemini-3-pro-preview\agent_files\target_stabilizers.txt"
BASELINE_FILE = r"data\gemini-3-pro-preview\agent_files\baseline.stim"
CANDIDATE_FILE = r"data\gemini-3-pro-preview\agent_files\candidate.stim"

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            n_targets = len(instr.targets_copy())
            cx_count += n_targets // 2
            volume += n_targets // 2 # CX is 2-qubit gate
        elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            n_targets = len(instr.targets_copy())
            volume += n_targets // 2
        elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "X", "Y", "Z", "I"]:
            n_targets = len(instr.targets_copy())
            volume += n_targets # 1-qubit gate
        elif instr.name in ["RX", "RY", "RZ"]:
            volume += len(instr.targets_copy())
        elif instr.name in ["TICK", "QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"]:
            pass
        else:
            # Other gates? MPP?
            pass
    return cx_count, volume

def main():
    # 1. Load Baseline
    try:
        with open(BASELINE_FILE, "r") as f:
            baseline = stim.Circuit(f.read())
        base_cx, base_vol = count_metrics(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        base_cx, base_vol = 999999, 999999

    # 2. Load Stabilizers
    try:
        with open(STABILIZERS_FILE, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        paulis = [stim.PauliString(line) for line in lines]
        # Allow underconstrained because maybe not full rank?
        tableau = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        print(f"Loaded {len(lines)} stabilizers.")
        
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    candidates = []

    # Method 1: Graph State
    try:
        # Check if RX is present in graph state
        circ_graph = tableau.to_circuit(method="graph_state")
        
        # Replace RX with H
        circ_str = str(circ_graph)
        if "RX" in circ_str:
            print("Replacing RX with H in graph state circuit.")
            circ_str = circ_str.replace("RX", "H")
            circ_graph = stim.Circuit(circ_str)
            
        cx, vol = count_metrics(circ_graph)
        print(f"Graph State: CX={cx}, Vol={vol}")
        candidates.append(("graph", circ_graph, cx, vol))
    except Exception as e:
        print(f"Graph state failed: {e}")

    # Method 2: Elimination
    try:
        circ_elim = tableau.to_circuit(method="elimination")
        cx, vol = count_metrics(circ_elim)
        print(f"Elimination: CX={cx}, Vol={vol}")
        candidates.append(("elim", circ_elim, cx, vol))
    except Exception as e:
        print(f"Elimination failed: {e}")

    # 3. Compare and Save Best
    better_candidates = []
    
    # We want strictly better:
    # cx < base_cx OR (cx == base_cx AND vol < base_vol)
    
    for name, circ, cx, vol in candidates:
        is_better = False
        if cx < base_cx:
            is_better = True
        elif cx == base_cx and vol < base_vol:
            is_better = True
            
        if is_better:
            better_candidates.append((name, circ, cx, vol))
            print(f"Found better candidate: {name} (CX={cx}, Vol={vol})")
    
    # Sort better candidates
    best_cand = None
    if better_candidates:
        better_candidates.sort(key=lambda x: (x[2], x[3]))
        best_cand = better_candidates[0]
        print(f"Best better candidate: {best_cand[0]}")
    else:
        # Fallback to best available
        if candidates:
            candidates.sort(key=lambda x: (x[2], x[3]))
            best_cand = candidates[0]
            print(f"No strictly better candidate. Using best available: {best_cand[0]}")
        else:
            print("No candidates generated.")
            return

    if best_cand:
        with open(CANDIDATE_FILE, "w") as f:
            f.write(str(best_cand[1]))
        print(f"Saved to {CANDIDATE_FILE}")

if __name__ == "__main__":
    main()
