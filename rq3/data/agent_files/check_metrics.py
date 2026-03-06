import stim

def get_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name == "CX":
            # CX targets are pairs
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            n = len(instr.targets_copy()) // 2
            vol += n
        else:
            # Single qubit gates or other
            n = len(instr.targets_copy())
            vol += n
    return cx, vol

def solve():
    # Load baseline
    baseline = stim.Circuit.from_file("data/agent_files/baseline.stim")
    base_cx, base_vol = get_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")

    # Load stabilizers
    with open("data/agent_files/target_stabilizers.txt") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    # Create tableau
    # stim.Tableau.from_stabilizers expects a list of PauliStrings
    ps = [stim.PauliString(s) for s in stabs]
    
    # Try naive synthesis
    try:
        tableau = stim.Tableau.from_stabilizers(ps, allow_underconstrained=True)
        # The tableau maps Z_i to S_i.
        # So applying the tableau operation to |0> prepares the state.
        # However, to_circuit gives the inverse operation usually?
        # Let's check.
        # Tableau.to_circuit() returns a circuit C such that C implements the tableau.
        # So C * Z_i * C' = S_i.
        # So C |0> is stabilized by S_i.
        
        # Stim's elimination method
        circuit = tableau.to_circuit("elimination")
        new_cx, new_vol = get_metrics(circuit)
        print(f"Naive synthesis: CX={new_cx}, Vol={new_vol}")
        
        if (new_cx < base_cx) or (new_cx == base_cx and new_vol < base_vol):
            print("IMPROVEMENT FOUND with naive synthesis")
            with open("data/agent_files/candidate_naive.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Naive synthesis is worse.")
            
    except Exception as e:
        print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    solve()
