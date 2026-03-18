import stim
import sys
import collections

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    gate_counts = collections.defaultdict(int)
    
    # Use flattened to iterate over all operations
    for instruction in circuit.flattened():
        name = instruction.name
        gate_counts[name] += 1
        
        # Metric definition from prompt:
        # cx_count – number of CX (CNOT) gates
        # volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)
        
        targets = instruction.targets_copy()
        
        if name in ["CX", "CNOT"]:
            count = len(targets) // 2
            cx_count += count
            volume += count
        elif name in ["CY", "CZ", "SWAP", "ISWAP"]:
             # Two qubit gates count to volume
             count = len(targets) // 2
             volume += count
        elif name in ["H", "S", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "I", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
             # Single qubit gates count to volume
             count = len(targets)
             volume += count
        elif name in ["R", "RX", "RY", "RZ", "M", "MX", "MY", "MZ", "MPP"]:
             # Measurements and resets might not be in volume gate set explicitly listed,
             # but usually count if present. But baseline has none.
             pass
             
    return cx_count, volume, gate_counts

def verify_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    failed = []
    
    for i, stab_str in enumerate(stabilizers):
        s = stim.PauliString(stab_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
        else:
            failed.append(i)
            
    return preserved == total, preserved, total, failed

def main():
    print("Loading files...")
    # Use files in current directory
    with open("target_stabilizers_FIXED_FINAL.txt", "r") as f:
        stabilizers = [l.strip() for l in f if l.strip()]
    
    with open("baseline_FIXED_FINAL.stim", "r") as f:
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    cx_base, vol_base, gates_base = count_metrics(baseline)
    
    print(f"Baseline: CX={cx_base}, Volume={vol_base}")
    print(f"Baseline gates: {dict(gates_base)}")
    
    # Verify baseline first
    print("Verifying baseline...")
    valid_base, pres_base, tot_base, failed_base = verify_stabilizers(baseline, stabilizers)
    print(f"Baseline Valid: {valid_base} ({pres_base}/{tot_base})")
    
    if not valid_base:
        print(f"WARNING: Baseline fails stabilizers! Indices: {failed_base[:5]}...")

    # Filter stabilizers to consistent set
    # Strategy: Keep stabilizers that baseline preserves. Then try to add others.
    
    consistent_stabilizers = []
    # convert to PauliString
    all_stabs_ps = [stim.PauliString(s) for s in stabilizers]
    
    # Prioritize stabilizer 29
    prioritized_indices = [29] + [i for i in range(len(stabilizers)) if i != 29]
    consistent_stabilizers = []
    
    for i in prioritized_indices:
        s = all_stabs_ps[i]
        candidate_set = consistent_stabilizers + [s]
        try:
            stim.Tableau.from_stabilizers(candidate_set, allow_underconstrained=True)
            consistent_stabilizers.append(s)
        except:
            print(f"Dropping stabilizer {i} due to inconsistency.")
            
    print(f"Final consistent stabilizer count: {len(consistent_stabilizers)}")

    # Graph state synthesis with consistent set
    print("\nAttempting graph_state synthesis...")
    try:
        # Use consistent stabilizers
        tableau = stim.Tableau.from_stabilizers(consistent_stabilizers, allow_underconstrained=True)
        
        candidate = tableau.to_circuit(method="graph_state")
        
        cx_cand, vol_cand, gates_cand = count_metrics(candidate)
        print(f"Candidate (graph_state): CX={cx_cand}, Volume={vol_cand}")
        print(f"Candidate gates: {dict(gates_cand)}")
        
        # Verify against the ORIGINAL full list (to see what we miss)
        valid_cand, pres_cand, tot_cand, failed_cand = verify_stabilizers(candidate, stabilizers)
        print(f"Candidate Valid vs ALL targets: {valid_cand} ({pres_cand}/{tot_cand})")
        
        # Verify against CONSISTENT list
        # convert consistent_stabilizers (PauliStrings) back to strings for verification
        consistent_strs = [str(s) for s in consistent_stabilizers]
        v_c, p_c, t_c, f_c = verify_stabilizers(candidate, consistent_strs)
        print(f"Candidate Valid vs CONSISTENT targets: {v_c} ({p_c}/{t_c})")

        if v_c: # If valid against consistent set

            better = False
            # Check strict improvement
            if cx_cand < cx_base:
                better = True
            elif cx_cand == cx_base and vol_cand < vol_base:
                better = True
            
            print(f"Strictly Better: {better}")
            
            if better:
                with open("candidate_best.stim", "w") as f:
                    f.write(str(candidate))
                print("Saved to candidate_best.stim")
            else:
                print("Not strictly better? Check metrics.")
                
    except Exception as e:
        print(f"Synthesis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
