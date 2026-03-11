import stim
import sys

def get_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            # usually CX is 2-qubit gate. If it has multiple targets like CX 0 1 2 3, it means CX 0 1, CX 2 3.
            # So targets/2.
            targets = instr.targets_copy()
            cx_count += len(targets) // 2
        
        # Volume: Count all gates.
        if instr.name not in ["QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK"]:
            # Count each individual gate application.
            # For 1-qubit gates, len(targets).
            # For 2-qubit gates, len(targets)/2 gates. But wait, volume counts total gates?
            # If CX 0 1 is one gate, then len(targets)/2.
            # If H 0 1 is two gates, then len(targets).
            # Let's assume standard gate counting.
            # 2-qubit gates: CX, CY, CZ, SWAP, ISWAP etc.
            if instr.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
                volume += len(instr.targets_copy()) // 2
            elif instr.name in ["MPP"]:
                # MPP is complicated. It's a measurement. Does it count as volume? The prompt says "CX, CY, CZ, H, S, SQRT_X, etc".
                # MPP is usually measurement. Measurements are usually excluded from volume or counted separately?
                # The prompt says "Do NOT introduce measurements... unless they already exist".
                # The baseline has no measurements.
                pass
            else:
                # 1-qubit gates
                volume += len(instr.targets_copy())
                
    return cx_count, volume

def main():
    # Load stabilizers
    with open("target_stabilizers_task.txt", "r") as f:
        stabs_text = f.read().replace("\n", "").replace(" ", "")
    stabs = [s for s in stabs_text.split(",") if s]

    print(f"Loaded {len(stabs)} stabilizers.")
    
    # Create Tableau
    try:
        pauli_stabs = [stim.PauliString(s.strip()) for s in stabs]
        tableau = stim.Tableau.from_stabilizers(pauli_stabs, allow_underconstrained=True)
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Load Baseline
    with open("baseline_task.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    base_cx, base_vol = get_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")

    # Generate Graph State Circuit
    cand_graph = tableau.to_circuit(method="graph_state")
    
    # Check if RX is present and replace with H if needed (assuming |0> input)
    # Graph state synthesis often assumes input is |+> which is H * |0>.
    # If the circuit starts with RX, it resets to |0> then rotates?
    # Actually, stim's graph state synthesis produces a circuit that prepares the state from a scratch state (all zero?).
    # Let's inspect the circuit.
    
    graph_cx, graph_vol = get_metrics(cand_graph)
    print(f"Graph State Candidate: CX={graph_cx}, Vol={graph_vol}")

    # Generate Elimination Circuit
    cand_elim = tableau.to_circuit(method="elimination")
    elim_cx, elim_vol = get_metrics(cand_elim)
    print(f"Elimination Candidate: CX={elim_cx}, Vol={elim_vol}")

    # Select best
    candidates = [("graph", cand_graph, graph_cx, graph_vol), ("elim", cand_elim, elim_cx, elim_vol)]
    
    best_cand = None
    
    for name, circ, cx, vol in candidates:
        if cx < base_cx or (cx == base_cx and vol < base_vol):
            print(f"Candidate {name} is strictly better locally.")
            # Check if we found a new best
            if best_cand is None:
                best_cand = (name, circ, cx, vol)
            else:
                # Compare with current best
                bc_name, bc_circ, bc_cx, bc_vol = best_cand
                if cx < bc_cx or (cx == bc_cx and vol < bc_vol):
                    best_cand = (name, circ, cx, vol)
    
    if best_cand:
        name, circ, cx, vol = best_cand
        print(f"Selected {name} as best candidate.")
        with open("candidate.stim", "w") as f:
            f.write(str(circ))
    else:
        print("No strictly better candidate found locally.")
        # Save graph state anyway to try, or maybe elimination?
        # If neither is better, I might need to optimize the better of the two.
        # But for now, let's save graph state if it's close.
        # Actually, let's just save the graph state one as 'candidate.stim' to see what `evaluate_optimization` says.
        # Maybe my local metric counting is slightly off vs the tool.
        with open("candidate.stim", "w") as f:
            f.write(str(cand_graph))

if __name__ == "__main__":
    main()
