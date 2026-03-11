import stim
import sys

def analyze_circuit(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        name = instr.name
        n_targets = len(instr.targets_copy())
        
        if name in ['CX', 'CNOT']:
            # CX is a 2-qubit gate. If there are multiple targets, it broadcasts.
            # Stim format: CX 0 1 2 3 means CX 0 1 then CX 2 3.
            # So pairs = n_targets / 2
            pairs = n_targets // 2
            cx_count += pairs
            volume += pairs
        elif name in ['CY', 'CZ', 'C_XYZ', 'C_ZYX']:
             pairs = n_targets // 2
             volume += pairs
        elif name in ['H', 'S', 'SQRT_X', 'X', 'Y', 'Z', 'I', 'S_DAG', 'SQRT_X_DAG', 'SQRT_Y', 'SQRT_Y_DAG', 'H_YZ', 'H_XY']:
             volume += n_targets
        elif name in ['RX', 'RY', 'RZ', 'R', 'M', 'MX', 'MY', 'MZ', 'MPP']:
             # These are not in the volume set described, or are resets/measurements
             # If they exist, we might want to flag them.
             pass
    return cx_count, volume

def main():
    try:
        with open("prompt_baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error reading baseline: {e}")
        return

    b_cx, b_vol = analyze_circuit(baseline)
    print(f"Baseline: CX={b_cx}, Vol={b_vol}")

    # Method 1: Tableau from circuit -> Graph state
    try:
        # Create tableau from the circuit
        tableau = stim.Tableau.from_circuit(baseline)
        
        # Method: Graph State
        cand1 = tableau.to_circuit(method='graph_state')
        
        # Post-process to remove resets if any
        # Replace RX with H, R with I (remove)
        new_cand1 = stim.Circuit()
        for instr in cand1:
            if instr.name == 'RX':
                new_cand1.append("H", instr.targets_copy())
            elif instr.name == 'R':
                # Reset to 0. If we are at 0 (start), this is I.
                # If in middle, it's a reset.
                # But graph state synthesis usually puts them at start.
                pass
            else:
                new_cand1.append(instr)
        cand1 = new_cand1
        
        c1_cx, c1_vol = analyze_circuit(cand1)
        print(f"Candidate 1 (Graph State): CX={c1_cx}, Vol={c1_vol}")
        
        with open("candidate_graph.stim", "w") as f:
            f.write(str(cand1))

        # Method: Elimination
        cand2 = tableau.to_circuit(method='elimination')
        c2_cx, c2_vol = analyze_circuit(cand2)
        print(f"Candidate 2 (Elimination): CX={c2_cx}, Vol={c2_vol}")

        if c1_cx < b_cx or (c1_cx == b_cx and c1_vol < b_vol):
            print("Candidate 1 is likely better.")
            
    except Exception as e:
        print(f"Error in optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
