
import stim
import sys

def get_metrics(circuit):
    cx = 0
    vol = 0
    # Iterate over instructions
    for instr in circuit:
        if instr.name == "CX":
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG", "XCZ", "XCY", "YCX", "YCZ"]:
             n = len(instr.targets_copy()) // 2
             vol += n
        elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "C_XYZ", "C_ZYX", "H_XY", "H_YZ", "H_ZX"]:
             n = len(instr.targets_copy())
             vol += n
        else:
             # Measurement, reset, noise
             pass
    return cx, vol

def count_cx(circuit):
    cx = 0
    for instr in circuit:
        if instr.name == "CX":
            cx += len(instr.targets_copy()) // 2
    return cx

def convert_cx_to_cz(circuit):
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "CX":
            targets = instr.targets_copy()
            for i in range(0, len(targets), 2):
                c = targets[i]
                t = targets[i+1]
                # CX c t = H t CZ c t H t
                new_circuit.append("H", [t])
                new_circuit.append("CZ", [c, t])
                new_circuit.append("H", [t])
        else:
            new_circuit.append(instr)
    return new_circuit

def solve():
    with open("data/agent_files/target_stabilizers.txt") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    ps = [stim.PauliString(s) for s in stabs]
    
    print(f"Loaded {len(ps)} stabilizers.")

    print("Loading data...")
    try:
        baseline = stim.Circuit.from_file("data/agent_files/baseline.stim")
        base_cx, base_vol = get_metrics(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        
        # Check baseline preservation
        sim = stim.TableauSimulator()
        sim.do(baseline)
        preserved = 0
        for i, s in enumerate(ps):
            if sim.peek_observable_expectation(s) == 1:
                preserved += 1
            else:
                # print(f"Baseline failed stabilizer {i}")
                pass
        print(f"Baseline preserves {preserved}/{len(ps)} stabilizers.")
        
    except Exception as e:
        print(f"Failed to load baseline: {e}")
        base_cx, base_vol = 999999, 999999
    
    best_cand = None
    best_metrics = (999999, 999999)
    
    methods = ["graph_state", "elimination"]
    
    for method in methods:
        print(f"Trying method: {method}")
        try:
            tableau = stim.Tableau.from_stabilizers(ps, allow_underconstrained=True, allow_redundant=True)
            circuit = tableau.to_circuit(method)
            
            # Check if valid
            sim = stim.TableauSimulator()
            sim.do(circuit)
            valid = True
            for s in ps:
                if sim.peek_observable_expectation(s) != 1:
                    valid = False
                    break
            
            if not valid:
                print(f"Method {method} failed validation.")
                continue
                
            # Calculate metrics
            cx, vol = get_metrics(circuit)
            print(f"Method {method}: CX={cx}, Vol={vol}")
            
            # Try to optimize CX -> CZ
            if cx > 0:
                print("Converting CX to CZ...")
                circuit_cz = convert_cx_to_cz(circuit)
                cx_cz, vol_cz = get_metrics(circuit_cz)
                print(f"Method {method} (CZ): CX={cx_cz}, Vol={vol_cz}")
                
                if cx_cz < best_metrics[0] or (cx_cz == best_metrics[0] and vol_cz < best_metrics[1]):
                    best_metrics = (cx_cz, vol_cz)
                    best_cand = circuit_cz
            
            if cx < best_metrics[0] or (cx == best_metrics[0] and vol < best_metrics[1]):
                best_metrics = (cx, vol)
                best_cand = circuit

        except Exception as e:
            print(f"Method {method} failed: {e}")

    if best_cand:
        print(f"Best candidate found: CX={best_metrics[0]}, Vol={best_metrics[1]}")
        with open("candidate.stim", "w") as f:
            f.write(str(best_cand))
    else:
        print("No valid candidate found.")

if __name__ == "__main__":
    solve()
