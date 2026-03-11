import stim
import sys
import os

def get_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            targets = instr.targets_copy()
            cx_count += len(targets) // 2
            volume += len(targets) // 2
        elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            volume += len(instr.targets_copy()) // 2
        elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "X", "Y", "Z", "I"]:
             volume += len(instr.targets_copy())
    return cx_count, volume

def clean_circuit(circuit):
    new_circ = stim.Circuit()
    for instr in circuit:
        if instr.name == "RX":
            targets = instr.targets_copy()
            new_circ.append("H", targets)
        elif instr.name in ["R", "RZ"]:
            pass
        elif instr.name == "RY":
             targets = instr.targets_copy()
             for t in targets:
                 new_circ.append("H", [t])
                 new_circ.append("S", [t])
        elif instr.name in ["M", "MX", "MY", "MZ", "MPP"]:
             pass
        else:
            new_circ.append(instr)
    return new_circ

def main():
    # Load all stabilizers
    try:
        with open("current_target_stabilizers.txt", "r") as f:
            lines = f.readlines()
        
        stabs_str = []
        for line in lines:
            line = line.strip().replace(" ", "")
            if line:
                if line.endswith(','):
                    line = line[:-1]
                parts = line.split(',')
                stabs_str.extend(parts)
        stabs_str = [s for s in stabs_str if s]
        pauli_stabs = [stim.PauliString(s) for s in stabs_str]
        print(f"Loaded {len(pauli_stabs)} stabilizers.")

    except Exception as e:
        print(f"Error processing stabilizers: {e}")
        return

    # Load Baseline and Filter Stabilizers
    try:
        with open("current_baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        base_cx, base_vol = get_metrics(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        
        # Check which stabilizers are preserved
        sim = stim.TableauSimulator()
        sim.do_circuit(baseline)
        
        consistent_stabs = []
        preserved_count = 0
        for i, s in enumerate(pauli_stabs):
            if sim.peek_observable_expectation(s) == 1:
                consistent_stabs.append(s)
                preserved_count += 1
            elif sim.peek_observable_expectation(s) == -1:
                # If it preserves the negative, maybe the sign was wrong in prompt?
                # But let's assume we want to match baseline.
                # If baseline has -1, we should target -1?
                # Construct tableau with -1?
                # PauliString doesn't support sign in constructor easily from string?
                # We can multiply by -1.
                consistent_stabs.append(s * -1)
                preserved_count += 1
                print(f"Stabilizer {i} preserved with -1 sign.")
            else:
                print(f"Stabilizer {i} NOT preserved (expectation 0). Skipping.")
        
        print(f"Baseline preserves {preserved_count}/{len(pauli_stabs)} (considering signs).")
        print(f"Using {len(consistent_stabs)} consistent stabilizers for generation.")
        
        # Create Tableau from consistent set
        tableau = stim.Tableau.from_stabilizers(consistent_stabs, allow_underconstrained=True)
        
    except Exception as e:
        print(f"Error processing baseline/stabilizers: {e}")
        return

    candidates = []

    # Method 1: Graph State
    try:
        print("Generating Graph State circuit...")
        raw_graph = tableau.to_circuit(method="graph_state")
        cand_graph = clean_circuit(raw_graph)
        graph_cx, graph_vol = get_metrics(cand_graph)
        print(f"Graph State: CX={graph_cx}, Vol={graph_vol}")
        candidates.append(("graph", cand_graph, graph_cx, graph_vol))
    except Exception as e:
        print(f"Error generating graph state: {e}")

    # Method 2: Elimination
    try:
        print("Generating Elimination circuit...")
        raw_elim = tableau.to_circuit(method="elimination")
        cand_elim = clean_circuit(raw_elim)
        elim_cx, elim_vol = get_metrics(cand_elim)
        print(f"Elimination: CX={elim_cx}, Vol={elim_vol}")
        candidates.append(("elim", cand_elim, elim_cx, elim_vol))
    except Exception as e:
        print(f"Error generating elimination: {e}")

    best_cand = None
    
    for name, circ, cx, vol in candidates:
        if best_cand is None:
            best_cand = (name, circ, cx, vol)
        else:
            b_name, b_circ, b_cx, b_vol = best_cand
            # lexicographic comparison
            if cx < b_cx or (cx == b_cx and vol < b_vol):
                best_cand = (name, circ, cx, vol)

    if best_cand:
        name, circ, cx, vol = best_cand
        print(f"Best candidate found: {name} (CX={cx}, Vol={vol})")
        with open("candidate.stim", "w") as f:
            f.write(str(circ))
        print("Written to candidate.stim")
    else:
        print("No candidates generated.")

if __name__ == "__main__":
    main()
