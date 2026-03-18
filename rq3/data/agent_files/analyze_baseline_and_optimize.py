import stim

def get_metrics(circuit):
    cx = 0
    volume = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            cx += len(instr.targets_copy()) // 2
            volume += len(instr.targets_copy()) // 2
        elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "CZ", "CY", "XCZ", "YCX"]:
            # All 1-qubit and 2-qubit gates count towards volume
            # Be careful with multi-target gates like H 0 1 2
            # Stim instructions store targets as a list.
            # For 1-qubit gates, len(targets) is the number of gates.
            # For 2-qubit gates (like CZ), len(targets)//2 is the number of gates.
            if instr.name in ["CZ", "CY", "XCZ", "YCX"]:
                volume += len(instr.targets_copy()) // 2
            else:
                volume += len(instr.targets_copy())
        # What about X, Y, Z, I? The prompt says "volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)". 
        # Usually Pauli gates are free or frame updates, but sometimes counted.
        # "etc" implies Clifford gates.
        # I'll count Paulis as volume for now, to be safe, or check if they are present.
        elif instr.name in ["X", "Y", "Z", "I"]:
            volume += len(instr.targets_copy())
        else:
            # TICK, SHIFT_COORDS, etc. likely don't count.
            pass
    return cx, volume

def run():
    c = stim.Circuit.from_file("baseline.stim")
    cx, vol = get_metrics(c)
    print(f"Baseline: CX={cx}, Vol={vol}")

    # Method 1: Elimination
    t = stim.Tableau.from_circuit(c)
    c_elim = t.to_circuit(method="elimination")
    cx_e, vol_e = get_metrics(c_elim)
    print(f"Elimination: CX={cx_e}, Vol={vol_e}")
    with open("candidate_elim.stim", "w") as f:
        f.write(str(c_elim))

    # Method 2: Graph State
    c_graph = t.to_circuit(method="graph_state")
    cx_g, vol_g = get_metrics(c_graph)
    print(f"Graph State: CX={cx_g}, Vol={vol_g}")
    with open("candidate_graph.stim", "w") as f:
        f.write(str(c_graph))

if __name__ == "__main__":
    run()
