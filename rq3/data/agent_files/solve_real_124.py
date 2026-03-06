import stim

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT", "CY", "CZ"]:
            n = len(instr.targets_copy())
            pairs = n // 2
            cx += pairs
            vol += pairs 
        elif instr.name in ["SWAP", "ISWAP"]:
            n = len(instr.targets_copy())
            pairs = n // 2
            # SWAP is usually 3 CNOTs or similar, but let's count as 1 volume op per pair for now?
            # Actually prompt says "volume - total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)".
            # So a SWAP is likely decomposed or counts as 1. Let's count as 1.
            vol += pairs
        elif instr.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            n = len(instr.targets_copy())
            vol += n
        elif instr.name in ["TICK", "QUBIT_COORDS", "SHIFT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"]:
            pass
        else:
            # Other gates
            n = len(instr.targets_copy())
            vol += n
            
    return cx, vol

def solve():
    # 1. Load Stabilizers
    with open("target_stabilizers_124.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))
        
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    # 2. Analyze Baseline
    try:
        with open("baseline_124.stim", "r") as f:
            base_circuit = stim.Circuit(f.read())
        
        base_cx, base_vol = count_metrics(base_circuit)
        print(f"Baseline Circuit: CX={base_cx}, Volume={base_vol}")
        
    except Exception as e:
        print(f"Baseline analysis failed: {e}")
        base_cx = 999999
        base_vol = 999999

    # 3. Synthesize Circuit
    best_circuit = None
    best_cx = base_cx
    best_vol = base_vol
    
    try:
        # Create tableau from stabilizers
        # allow_underconstrained=True because 34 stabilizers for 35 qubits (one logical qubit)
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        
        methods = ["graph_state", "elimination"] # graph_state is usually better for stabilizers
        
        for method in methods:
            try:
                print(f"Trying synthesis method: {method}")
                circuit = tableau.to_circuit(method=method)
                
                cx, vol = count_metrics(circuit)
                print(f"Method {method}: CX={cx}, Vol={vol}")
                
                if cx < best_cx or (cx == best_cx and vol < best_vol):
                    best_cx = cx
                    best_vol = vol
                    best_circuit = circuit
                    print(f"New best found with method {method}")
                    
            except Exception as e:
                print(f"Method {method} failed: {e}")
                
    except Exception as e:
        print(f"Synthesis failed: {e}")

    if best_circuit:
        with open("candidate_124.stim", "w") as f:
            f.write(str(best_circuit))
        print("Wrote best candidate to candidate_124.stim")
    else:
        print("No improvement found.")

if __name__ == "__main__":
    solve()
