import stim
import sys
import random
import os

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instruction in circuit.flattened():
        name = instruction.name
        if name in ["CX", "CNOT", "CY", "CZ", "ISWAP", "SWAP"]:
            n = len(instruction.targets_copy()) // 2
            cx += n * (1 if name in ["CX", "CNOT"] else 0) # Only count CX/CNOT for cx_count?
            # Wait, prompt says: "cx_count – number of CX (CNOT) gates".
            # "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)"
            vol += n
        elif name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]:
            n = len(instruction.targets_copy())
            vol += n
        elif name in ["TICK", "SHIFT_COORDS", "QUOTED_STRING_ARGS", "DETECTOR", "OBSERVABLE_INCLUDE", "MPP"]:
            pass
        else:
             # Measurements? 
             pass
    return cx, vol

def main():
    print("Loading baseline...")
    with open("current_task_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    base_cx, base_vol = count_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    print("Loading stabilizers...")
    with open("current_task_stabilizers.txt", "r") as f:
        stabilizers_str = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(stabilizers_str)} stabilizers.")

    best_cx = base_cx
    best_vol = base_vol
    best_circuit = None
    best_method = None

    # Helper to update best
    def update_best(circuit, method_name):
        nonlocal best_cx, best_vol, best_circuit, best_method
        cx, vol = count_metrics(circuit)
        # print(f"  {method_name}: CX={cx}, Vol={vol}")
        
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
            with open("best_candidate.stim", "w") as f:
                f.write(str(circuit))
        return cx, vol

    # Strategy 1: Baseline flattened (just in case)
    # update_best(baseline.flattened(), "Baseline Flattened")

    # Strategy 2: Direct Synthesis (Elimination)
    try:
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers_str]
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="elimination")
        update_best(circuit, "Direct Elimination")
    except Exception as e:
        print(f"Direct Elimination failed: {e}")

    # Strategy 3: Direct Synthesis (Graph State)
    try:
        circuit = tableau.to_circuit(method="graph_state")
        update_best(circuit, "Direct Graph State")
    except Exception as e:
        print(f"Direct Graph State failed: {e}")

    # Strategy 4: Permutations with Elimination
    print("Trying permutations...")
    strategies = [
        ("reverse", lambda s: list(reversed(s))),
        ("sort_weight", lambda s: sorted(s, key=lambda x: sum(1 for c in x if c in 'XYZ'))),
        ("sort_weight_desc", lambda s: sorted(s, key=lambda x: -sum(1 for c in x if c in 'XYZ'))),
        ("sort_first_x", lambda s: sorted(s, key=lambda x: x.find('X') if 'X' in x else 999)),
        ("sort_first_z", lambda s: sorted(s, key=lambda x: x.find('Z') if 'Z' in x else 999)),
    ]
    
    for i in range(50):
        strategies.append((f"shuffle_{i}", lambda s: random.sample(s, len(s))))

    for name, strategy in strategies:
        try:
            permuted_strs = strategy(stabilizers_str)
            permuted_paulis = [stim.PauliString(s) for s in permuted_strs]
            tableau = stim.Tableau.from_stabilizers(permuted_paulis, allow_redundant=True, allow_underconstrained=True)
            
            # Try elimination
            circuit = tableau.to_circuit(method="elimination")
            update_best(circuit, f"Elimination ({name})")
            
            # Try graph state
            try:
                circuit = tableau.to_circuit(method="graph_state")
                update_best(circuit, f"Graph State ({name})")
            except:
                pass
                
        except Exception as e:
            pass

    print(f"Final Best: CX={best_cx}, Vol={best_vol} (Method: {best_method})")
    
    if best_circuit is None:
        print("No improvement found.")
        # Output baseline as candidate just to be safe, but strictly we need better.
        with open("best_candidate.stim", "w") as f:
            f.write(str(baseline))
    else:
        print("Improvement found!")

if __name__ == "__main__":
    main()
