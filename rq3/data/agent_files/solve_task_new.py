import stim
import sys

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif instr.name in ["H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I"]:
             n = len(instr.targets_copy())
             vol += n
        elif instr.name == "CZ":
             n = len(instr.targets_copy()) // 2
             # If we treat CZ as 1 CX + 2 H (volume 3)
             cx += n
             vol += 3 * n
        elif instr.name == "RX": # Reset X, treat as H if input is |0>
             n = len(instr.targets_copy())
             vol += n
        else:
             # Other gates
             n = len(instr.targets_copy())
             vol += n
    return cx, vol

def convert_to_cx(circuit):
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                # CZ = H(t) CX(c, t) H(t)
                new_circuit.append("H", [t])
                new_circuit.append("CX", [c, t])
                new_circuit.append("H", [t])
        elif instr.name == "RX":
            # RX resets to |+>. If we assume input is |0>, this is H.
            new_circuit.append("H", instr.targets_copy())
        else:
            new_circuit.append(instr.name, instr.targets_copy(), instr.gate_args_copy())
    return new_circuit

def main():
    # 1. Load baseline
    with open("baseline_circuit_new.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    base_cx, base_vol = count_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Volume={base_vol}, Qubits={baseline.num_qubits}")

    # 2. Load stabilizers
    stabilizers = []
    with open("target_stabilizers_new.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))
    
    print(f"Loaded {len(stabilizers)} stabilizers.")

    best_circuit = None
    best_cx = base_cx
    best_vol = base_vol

    # 3. Synthesize with elimination
    try:
        print("Trying elimination method...")
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        # Note: from_stabilizers might pick arbitrary phases if underconstrained.
        # But here we have X and Z stabilizers which might fix phases?
        # The prompt target stabilizers have no signs (implied +).
        # stim.PauliString(line) handles signs if present.
        # If no signs in text, it defaults to +.
        
        circ_elim = tableau.to_circuit(method="elimination")
        # Remove explicit R gates if any (elimination usually uses H, S, CX, maybe M/R?)
        # elimination usually produces unitary.
        cx, vol = count_metrics(circ_elim)
        print(f"Elimination: CX={cx}, Volume={vol}")
        
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            best_circuit = circ_elim
            best_cx = cx
            best_vol = vol
            print("Elimination is better.")
    except Exception as e:
        print(f"Elimination failed: {e}")

    # 4. Synthesize with graph_state
    try:
        print("Trying graph_state method...")
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circ_graph = tableau.to_circuit(method="graph_state")
        circ_graph_cx = convert_to_cx(circ_graph)
        cx, vol = count_metrics(circ_graph_cx)
        print(f"Graph State (converted): CX={cx}, Volume={vol}")
        
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            best_circuit = circ_graph_cx
            best_cx = cx
            best_vol = vol
            print("Graph State is better.")
    except Exception as e:
        print(f"Graph State failed: {e}")

    if best_circuit:
        print("Saving best candidate.")
        with open("candidate.stim", "w") as f:
            f.write(str(best_circuit))
    else:
        print("No improvement found.")

if __name__ == "__main__":
    main()
