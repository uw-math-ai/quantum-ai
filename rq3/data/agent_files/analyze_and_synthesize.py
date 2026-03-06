
import stim
import sys

def count_cx(circuit):
    count = 0
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT"]:
            count += len(instruction.targets_copy()) // 2
    return count

def get_volume(circuit):
    count = 0
    gate_set = ["CX", "CNOT", "CY", "CZ", "H", "S", "S_DAG", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG", "X", "Y", "Z", "I"]
    for instruction in circuit:
        if instruction.name in gate_set:
            targets = instruction.targets_copy()
            if instruction.name in ["CX", "CNOT", "CY", "CZ"]:
                 count += len(targets) // 2
            else:
                 count += len(targets)
    return count

def read_stabilizers(path):
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def main():
    stabilizers = read_stabilizers("prompt_stabilizers.txt")
    baseline = stim.Circuit.from_file("prompt_baseline.stim")
    
    b_cx = count_cx(baseline)
    b_vol = get_volume(baseline)
    print(f"Baseline CX: {b_cx}")
    print(f"Baseline Volume: {b_vol}")
    
    # Check baseline preservation
    sim = stim.TableauSimulator()
    sim.do(baseline)
    preserved = 0
    stab_objs = []
    for s in stabilizers:
        p = stim.PauliString(s)
        stab_objs.append(p)
        if sim.peek_observable_expectation(p) == 1:
            preserved += 1
    
    print(f"Baseline preserved: {preserved}/{len(stabilizers)}")
    
    if preserved != len(stabilizers):
        print("WARNING: Baseline does not preserve all stabilizers!")

    # Attempt Synthesis
    try:
        # Method 1: Gaussian Elimination
        tableau = stim.Tableau.from_stabilizers(stab_objs, allow_underconstrained=True)
        cand1 = tableau.to_circuit("elimination")
        
        c1_cx = count_cx(cand1)
        c1_vol = get_volume(cand1)
        print(f"Candidate 1 (Elimination) CX: {c1_cx}, Volume: {c1_vol}")
        
        # Method 2: Graph State
        cand2_raw = tableau.to_circuit("graph_state")
        
        # Post-process: Replace RX with H, remove TICK
        cand2 = stim.Circuit()
        for inst in cand2_raw:
            if inst.name == "RX":
                # Replace RX with H on the same targets
                cand2.append("H", inst.targets_copy())
            elif inst.name == "TICK":
                continue
            else:
                cand2.append(inst)
                
        c2_cx = count_cx(cand2)
        c2_vol = get_volume(cand2)
        print(f"Candidate 2 (Graph State, clean) CX: {c2_cx}, Volume: {c2_vol}")
        
        # Compare
        best_cand = None
        best_metrics = (b_cx, b_vol)
        best_name = "Baseline"
        
        # Check Candidate 1
        if (c1_cx < b_cx) or (c1_cx == b_cx and c1_vol < b_vol):
             # Verify it works
             sim1 = stim.TableauSimulator()
             sim1.do(cand1)
             p1 = 0
             for s in stab_objs:
                 if sim1.peek_observable_expectation(s) == 1:
                     p1 += 1
             if p1 == len(stabilizers):
                 best_cand = cand1
                 best_metrics = (c1_cx, c1_vol)
                 best_name = "Elimination"
                 
        # Check Candidate 2
        if (c2_cx < best_metrics[0]) or (c2_cx == best_metrics[0] and c2_vol < best_metrics[1]):
             sim2 = stim.TableauSimulator()
             sim2.do(cand2)
             p2 = 0
             for s in stab_objs:
                 if sim2.peek_observable_expectation(s) == 1:
                     p2 += 1
             if p2 == len(stabilizers):
                 best_cand = cand2
                 best_metrics = (c2_cx, c2_vol)
                 best_name = "Graph State"

        print(f"Best strategy: {best_name}")
        
        if best_cand:
            with open("best_candidate.stim", "w") as f:
                f.write(str(best_cand))
            print("Saved best_candidate.stim")
        else:
            print("No improvement found.")
            
    except Exception as e:
        print(f"Synthesis error: {e}")

if __name__ == "__main__":
    main()
