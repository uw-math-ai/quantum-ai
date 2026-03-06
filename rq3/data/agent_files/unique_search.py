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
    # Simple peephole optimization
    instructions = list(circuit)
    new_instructions = []
    
    i = 0
    while i < len(instructions):
        inst = instructions[i]
        
        # Check for self-inverse gates adjacent
        if i + 1 < len(instructions):
            next_inst = instructions[i+1]
            if inst.name == next_inst.name and inst.targets_copy() == next_inst.targets_copy():
                if inst.name in ["H", "CX", "CZ", "X", "Y", "Z"]: # Self-inverse
                    i += 2
                    continue
        
        new_instructions.append(inst)
        i += 1
        
    # Reconstruct
    new_circ = stim.Circuit()
    for inst in new_instructions:
        new_circ.append(inst)
    return new_circ

def main():
    print("Loading data...")
    with open("unique_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    with open("unique_baseline.stim", "r") as f:
        baseline_text = f.read()
    
    baseline_circuit = stim.Circuit(baseline_text)
    base_cx, base_vol = count_gates(baseline_circuit)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}")
    
    if not check_stabilizers(baseline_circuit, stabilizers):
        print("CRITICAL WARNING: Baseline does NOT preserve stabilizers!")
    else:
        print("Baseline is valid.")
    
    best_cx = base_cx
    best_vol = base_vol
    best_circuit = None
    found_better = False

    # Attempt 1: Default Elimination
    try:
        stim_stabs = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True)
        circ = tableau.to_circuit(method="elimination")
        
        # Optimize simple
        circ = optimize_circuit_simple(circ)
        
        cx, vol = count_gates(circ)
        print(f"Default Elimination: CX={cx}, Vol={vol}")
        
        if cx < best_cx or (cx == best_cx and vol < best_vol):
            print("Found improvement with Default Elimination!")
            best_cx = cx
            best_vol = vol
            best_circuit = circ
            found_better = True
        
        # Also try graph_state if possible
        try:
             circ_g = tableau.to_circuit(method="graph_state")
             circ_g = optimize_circuit_simple(circ_g)
             cx_g, vol_g = count_gates(circ_g)
             print(f"Default Graph State: CX={cx_g}, Vol={vol_g}")
             if cx_g < best_cx or (cx_g == best_cx and vol_g < best_vol):
                print("Found improvement with Default Graph State!")
                best_cx = cx_g
                best_vol = vol_g
                best_circuit = circ_g
                found_better = True
        except Exception as e:
             # print(f"Graph state failed: {e}")
             pass

    except Exception as e:
        print(f"Default failed: {e}")

    # Attempt 2: Search with shuffling
    print("Starting shuffle search (2000 iterations)...")
    for i in range(2000):
        try:
            random.shuffle(stabilizers)
            stim_stabs = [stim.PauliString(s) for s in stabilizers]
            tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True)
            circ = tableau.to_circuit(method="elimination")
            
            # Optimize simple
            circ = optimize_circuit_simple(circ)

            cx, vol = count_gates(circ)
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Iteration {i}: Found improvement! CX={cx}, Vol={vol}")
                
                # Check validity
                if check_stabilizers(circ, stabilizers):
                     print("Valid improvement confirmed!")
                     best_cx = cx
                     best_vol = vol
                     best_circuit = circ
                     found_better = True
                     
                     with open("candidate.stim", "w") as f:
                         f.write(str(best_circuit))
                else:
                     print("Invalid circuit. Ignoring.")
                     
        except Exception as e:
            pass
            
    if found_better and best_circuit:
        print(f"Best found: CX={best_cx}, Vol={best_vol}")
        with open("candidate.stim", "w") as f:
            f.write(str(best_circuit))
    else:
        print("No improvement found.")
        # If no improvement, ensure candidate.stim has the baseline or best valid
        if best_circuit is None and check_stabilizers(baseline_circuit, stabilizers):
             with open("candidate.stim", "w") as f:
                 f.write(str(baseline_circuit))

if __name__ == "__main__":
    main()
