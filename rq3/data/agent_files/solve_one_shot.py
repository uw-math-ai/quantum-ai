import stim

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        else:
            # simple volume approx
            vol += len(instr.targets_copy())
    return cx, vol

def solve():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\target_stabilizers.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Parse stabilizers
    stabilizers = []
    for l in lines:
        stabilizers.append(stim.PauliString(l))
    
    # Check if they commute
    for i in range(len(stabilizers)):
        for j in range(i+1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Stabilizers {i} and {j} do not commute!")
                return

    # Synthesize
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit("graph_state") 
    except Exception as e:
        print(f"Synthesis failed: {e}")
        # Try without graph_state method first to see default
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit()

    # Get baseline metrics
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\baseline.stim") as f:
        base_circuit = stim.Circuit(f.read())
    
    base_cx, base_vol = get_metrics(base_circuit)
    new_cx, new_vol = get_metrics(circuit)
    
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    print(f"Synthesized: CX={new_cx}, Vol={new_vol}")

    if (new_cx < base_cx) or (new_cx == base_cx and new_vol < base_vol):
        print("IMPROVEMENT FOUND")
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate.stim", "w") as f:
            f.write(str(circuit))
    else:
        print("No improvement with default synthesis.")
        # Try another method: "gaussian"
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit2 = tableau.to_circuit(method="elimination")
        cx2, vol2 = get_metrics(circuit2)
        print(f"Elimination method: CX={cx2}, Vol={vol2}")
        
        if (cx2 < base_cx) or (cx2 == base_cx and vol2 < base_vol):
             print("IMPROVEMENT FOUND (elimination)")
             with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate.stim", "w") as f:
                f.write(str(circuit2))

if __name__ == "__main__":
    solve()
