import stim
import sys
import heapq

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name == "CX" or instruction.name == "CNOT":
            count += len(instruction.targets_copy()) // 2
    return count

def count_volume(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT", "CY", "CZ", "H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
            if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
                count += len(instruction.targets_copy()) // 2
            else:
                count += len(instruction.targets_copy())
    return count

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = True
    failed_count = 0
    for stab_str in stabilizers:
        pauli = stim.PauliString(stab_str)
        if sim.peek_observable_expectation(pauli) != 1:
            preserved = False
            failed_count += 1
    return preserved, failed_count

def optimize():
    # Load baseline
    try:
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        print("Loaded baseline.stim")
    except:
        print("Could not load baseline.stim")
        return

    # Load stabilizers
    stabilizers = []
    with open("target_stabilizers.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                stabilizers.append(line)
    
    # Analyze baseline
    b_cx = count_cx(baseline)
    b_vol = count_volume(baseline)
    print(f"Baseline: CX={b_cx}, Vol={b_vol}")
    
    valid, failed = check_stabilizers(baseline, stabilizers)
    print(f"Baseline Valid: {valid} (failed: {failed})")
    
    best_circuit = baseline
    best_cx = b_cx
    best_vol = b_vol
    
    candidates = []
    
    # Method 1: Resynthesis from Stabilizers (Graph State)
    try:
        print("Attempting synthesis from stabilizers (graph_state)...")
        stim_stabs = [stim.PauliString(s) for s in stabilizers]
        tableau = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True, allow_redundant=True)
        cand1 = tableau.to_circuit("graph_state")
        candidates.append(("Stab_GraphState", cand1))
    except Exception as e:
        print(f"Stab_GraphState failed: {e}")

    # Method 2: Resynthesis from Stabilizers (Elimination)
    try:
        print("Attempting synthesis from stabilizers (elimination)...")
        cand2 = tableau.to_circuit("elimination")
        candidates.append(("Stab_Elimination", cand2))
    except Exception as e:
        print(f"Stab_Elimination failed: {e}")
        
    # Method 3: Resynthesis from Baseline Tableau (Graph State)
    try:
        print("Attempting synthesis from baseline tableau (graph_state)...")
        t_base = baseline.to_tableau()
        cand3 = t_base.to_circuit("graph_state")
        candidates.append(("Base_GraphState", cand3))
    except Exception as e:
        print(f"Base_GraphState failed: {e}")

    # Method 4: Resynthesis from Baseline Tableau (Elimination)
    try:
        print("Attempting synthesis from baseline tableau (elimination)...")
        cand4 = t_base.to_circuit("elimination")
        candidates.append(("Base_Elimination", cand4))
    except Exception as e:
        print(f"Base_Elimination failed: {e}")

    # Evaluate candidates
    for name, cand in candidates:
        cx = count_cx(cand)
        vol = count_volume(cand)

        # Count CZs
        cz = 0
        for instr in cand:
            if instr.name == "CZ":
                cz += len(instr.targets_copy()) // 2
        
        # Estimate decomposed CX
        decomposed_cx = cx + cz

        print(f"Candidate {name}: CX={cx}, CZ={cz}, Decomposed_CX={decomposed_cx}, Vol={vol}")
        
        # Check validity
        is_valid, n_failed = check_stabilizers(cand, stabilizers)
        
        if is_valid:
            better = False
            if cx < best_cx:
                better = True
            elif cx == best_cx and vol < best_vol:
                better = True
            
            if better:
                print(f"  VALID & BETTER! (CX: {best_cx}->{cx}, Vol: {best_vol}->{vol})")
                best_circuit = cand
                best_cx = cx
                best_vol = vol
            else:
                 print(f"  Valid but not better.")
        else:
            print(f"  INVALID (failed {n_failed} stabilizers)")

    # Save best
    print(f"Best circuit: CX={best_cx}, Vol={best_vol}")
    with open("best_candidate.stim", "w") as f:
        f.write(str(best_circuit))

if __name__ == "__main__":
    optimize()
