import stim
import sys
import random

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit.flattened():
        name = instruction.name
        if name in ["CX", "CNOT", "CY", "CZ", "ISWAP", "SWAP"]:
            n = len(instruction.targets_copy()) // 2
            cx += n * (1 if name in ["CX", "CNOT"] else 0)
            vol += n
        elif name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            n = len(instruction.targets_copy())
            vol += n
        elif name in ["TICK", "SHIFT_COORDS", "QUOTED_STRING_ARGS", "DETECTOR", "OBSERVABLE_INCLUDE", "MPP"]:
            pass
        else:
             pass
    return cx, vol

def main():
    print("Loading baseline...")
    with open("baseline_v100.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    base_cx, base_vol = count_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    print("Loading stabilizers...")
    with open("target_stabilizers_v100.txt", "r") as f:
        content = f.read().strip()
        stabilizers_str = [s.strip() for s in content.split(',') if s.strip()]
    
    print(f"Loaded {len(stabilizers_str)} stabilizers.")

    best_cx = base_cx
    best_vol = base_vol
    best_circuit = None
    best_method = None

    def update_best(circuit, method_name):
        nonlocal best_cx, best_vol, best_circuit, best_method
        cx, vol = count_metrics(circuit)
        
        is_better = False
        if cx < best_cx:
            is_better = True
        elif cx == best_cx and vol < best_vol:
            is_better = True
            
        if is_better:
            print(f"  [IMPROVED] {method_name}: CX={cx}, Vol={vol} (was {best_cx}, {best_vol})")
            best_cx = cx
            best_vol = vol
            best_circuit = circuit
            best_method = method_name
            with open("candidate_v100.stim", "w") as f:
                f.write(str(circuit))
        return cx, vol

    # Try Direct Synthesis (Graph State)
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers_str]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        update_best(circuit, "Direct Graph State")
    except Exception as e:
        print(f"Direct Graph State failed: {e}")

    print(f"Final Best: CX={best_cx}, Vol={best_vol} (Method: {best_method})")
    
    if best_circuit is None:
        print("No improvement found. Saving baseline as candidate_v100.stim (but it won't pass strictly better check).")
        with open("candidate_v100.stim", "w") as f:
            f.write(str(baseline))
    else:
        print("Improvement found and saved to candidate_v100.stim")

if __name__ == "__main__":
    main()
