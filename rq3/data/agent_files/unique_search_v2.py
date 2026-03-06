import stim
import random
import sys

def count_gates(circuit):
    cx_count = 0
    volume = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT"]:
            n = len(instruction.targets_copy()) // 2
            cx_count += n
            volume += n
        elif instruction.name in ["H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "X", "Y", "Z", "I", "SQRT_Y", "SQRT_Y_DAG", "CZ", "CY"]:
             volume += len(instruction.targets_copy())
    return cx_count, volume

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    for stab_str in stabilizers:
        if sim.peek_observable_expectation(stim.PauliString(stab_str)) != 1:
            return False
    return True

def optimize_circuit_simple(circuit):
    instructions = list(circuit)
    new_instructions = []
    
    i = 0
    while i < len(instructions):
        inst = instructions[i]
        
        if i + 1 < len(instructions):
            next_inst = instructions[i+1]
            if inst.name == next_inst.name and inst.targets_copy() == next_inst.targets_copy():
                if inst.name in ["H", "CX", "CZ", "X", "Y", "Z"]: 
                    i += 2
                    continue
        
        new_instructions.append(inst)
        i += 1
        
    new_circ = stim.Circuit()
    for inst in new_instructions:
        new_circ.append(inst)
    return new_circ

def main():
    print("Loading data...")
    with open("fixed_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    with open("unique_baseline.stim", "r") as f:
        baseline_text = f.read()
    
    baseline_circuit = stim.Circuit(baseline_text)
    base_cx, base_vol = count_gates(baseline_circuit)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    # We assume fixed_stabilizers are valid for baseline (computed from it)
    
    best_cx = base_cx
    best_vol = base_vol
    best_circuit = None
    found_better = False

    # Attempt 1: Graph State Synthesis (likely best if works)
    try:
        stim_stabs = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True)
        circ_g = tableau.to_circuit(method="graph_state")
        circ_g = optimize_circuit_simple(circ_g)
        cx_g, vol_g = count_gates(circ_g)
        print(f"Graph State: CX={cx_g}, Vol={vol_g}")
        
        if cx_g < best_cx or (cx_g == best_cx and vol_g < best_vol):
            print("Found improvement with Graph State!")
            best_cx = cx_g
            best_vol = vol_g
            best_circuit = circ_g
            found_better = True
    except Exception as e:
        print(f"Graph state failed: {e}")

    # Attempt 2: Elimination (Default)
    try:
        stim_stabs = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True)
        circ = tableau.to_circuit(method="elimination")
        circ = optimize_circuit_simple(circ)
        cx, vol = count_gates(circ)
        print(f"Elimination: CX={cx}, Vol={vol}")
        
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            print("Found improvement with Elimination!")
            best_cx = cx
            best_vol = vol
            best_circuit = circ
            found_better = True
    except Exception as e:
        print(f"Elimination failed: {e}")

    # Attempt 3: Shuffle Search
    print("Starting shuffle search (1000 iterations)...")
    for i in range(1000):
        try:
            random.shuffle(stabilizers)
            stim_stabs = [stim.PauliString(s) for s in stabilizers]
            tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True)
            # Try both methods
            methods = ["elimination"]
            # Graph state usually doesn't depend on order of stabilizers for the output structure? 
            # Actually, to_circuit(graph_state) requires specific structure.
            
            for method in methods:
                circ = tableau.to_circuit(method=method)
                circ = optimize_circuit_simple(circ)
                cx, vol = count_gates(circ)
                
                if cx < best_cx or (cx == best_cx and vol < best_vol):
                    print(f"Iteration {i} ({method}): Found improvement! CX={cx}, Vol={vol}")
                    
                    if check_stabilizers(circ, stabilizers):
                         print("Valid improvement confirmed!")
                         best_cx = cx
                         best_vol = vol
                         best_circuit = circ
                         found_better = True
                         with open("candidate.stim", "w") as f:
                             f.write(str(best_circuit))
                    
        except Exception as e:
            pass
            
    if found_better and best_circuit:
        print(f"Best found: CX={best_cx}, Vol={best_vol}")
        with open("candidate.stim", "w") as f:
            f.write(str(best_circuit))
    else:
        print("No improvement found.")
        # If no improvement, candidate.stim should contain baseline
        # But wait, if found_better is False, we should check if baseline is even valid w.r.t the fixed stabilizers.
        # It is by definition.
        if best_circuit is None:
             with open("candidate.stim", "w") as f:
                 f.write(str(baseline_circuit))

if __name__ == "__main__":
    main()
