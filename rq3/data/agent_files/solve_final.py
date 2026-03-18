import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count += len(instr.targets_copy()) // 2
    return count

def count_vol(circuit):
    vol = 0
    for instr in circuit:
        n = len(instr.targets_copy())
        if instr.name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
            vol += n // 2
        else:
            vol += n
    return vol

def main():
    try:
        # Load files
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\current_task_baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\current_task_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        
        targets = [stim.PauliString(l) for l in lines]
        num_qubits = len(targets[0])
        print(f"Num qubits: {num_qubits}")
        print(f"Num stabilizers: {len(targets)}")
        
        base_cx = count_cx(baseline)
        base_vol = count_vol(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        
        # Verify baseline
        sim = stim.TableauSimulator()
        sim.do(baseline)
        preserved_count = 0
        for t in targets:
            if sim.peek_observable_expectation(t) == 1:
                preserved_count += 1
        
        print(f"Baseline preserves {preserved_count}/{len(targets)} targets.")
        
        # We assume the baseline defines the correct behavior.
        # So we use the baseline's tableau for synthesis.
        tableau = stim.Tableau.from_circuit(baseline)
            
        # Try 'graph_state' method first (if available)
        methods = ["graph_state", "elimination"]
        best_circuit = None
        best_cx = base_cx
        best_vol = base_vol
        found_better = False
        
        for m in methods:
            try:
                print(f"Trying synthesis method: {m}")
                cand = tableau.to_circuit(method=m)
                
                # Check validity of candidate against BASELINE's behavior
                # The candidate is synthesized from baseline's tableau, so it SHOULD be valid by construction.
                # But we verify it preserves the SAME targets as baseline.
                sim_cand = stim.TableauSimulator()
                sim_cand.do(cand)
                cand_preserved = 0
                for t in targets:
                    if sim_cand.peek_observable_expectation(t) == 1:
                        cand_preserved += 1
                
                print(f"  Method {m} preserves {cand_preserved}/{len(targets)} targets.")
                
                if cand_preserved < preserved_count:
                    print(f"  Method {m} is WORSE than baseline in preservation. Skipping.")
                    continue
                    
                c_cx = count_cx(cand)
                c_vol = count_vol(cand)
                print(f"  Method {m}: CX={c_cx}, Vol={c_vol}")
                
                if c_cx < best_cx or (c_cx == best_cx and c_vol < best_vol):
                    best_cx = c_cx
                    best_vol = c_vol
                    best_circuit = cand
                    found_better = True
                    print(f"  -> New best!")
            except Exception as e:
                print(f"  Method {m} failed: {e}")
                
        if found_better:
            print("Writing best candidate to best_candidate.stim")
            with open("best_candidate.stim", "w") as f:
                f.write(str(best_circuit))
        else:
            print("No improvement found.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
