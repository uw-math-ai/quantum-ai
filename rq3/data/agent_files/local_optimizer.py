import stim

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "CXSWAP", "SWAPCX", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            count += len(op.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for op in circuit:
        if op.name in ["QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "SHIFT_COORDS", "TICK"]:
            continue
        targets = op.targets_copy()
        if op.name in ["CX", "CNOT", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            count += len(targets) // 2
        else:
            count += len(targets)
    return count

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for stab in stabilizers:
        if sim.peek_observable_expectation(stab) != 1:
            return False
    return True

def load_stabilizers(filename):
    stabilizers = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(stim.PauliString(line))
    return stabilizers

def solve():
    with open("current_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    stabilizers = load_stabilizers("current_stabilizers.txt")
    
    base_cx = count_cx(baseline)
    base_vol = count_volume(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse() 
    # Wait, sim.current_inverse_tableau() gives T^-1. We want T.
    # So .inverse() is correct.
    
    candidates = []
    
    # Method 1: Elimination
    try:
        c1 = tableau.to_circuit(method="elimination")
        candidates.append(("elimination", c1))
    except Exception as e:
        print(f"Error with elimination: {e}")

    # Method 2: Graph State
    try:
        c2 = tableau.to_circuit(method="graph_state")
        candidates.append(("graph_state", c2))
    except Exception as e:
        print(f"Error with graph_state: {e}")
        
    best_circuit = None
    best_name = "baseline"
    best_cx = base_cx
    best_vol = base_vol
    found_better = False

    for name, cand in candidates:
        if not check_stabilizers(cand, stabilizers):
            print(f"Candidate {name} INVALID (stabilizers failed)")
            continue
            
        cx = count_cx(cand)
        vol = count_volume(cand)
        print(f"Candidate {name}: CX={cx}, Vol={vol}")
        
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            best_circuit = cand
            best_name = name
            best_cx = cx
            best_vol = vol
            found_better = True
            
    if found_better:
        print(f"STRICT IMPROVEMENT FOUND: {best_name}")
        print(f"New CX={best_cx}, Vol={best_vol}")
        with open("best_candidate.stim", "w") as f:
            f.write(str(best_circuit))
    else:
        print("No strict improvement found.")

if __name__ == "__main__":
    solve()
