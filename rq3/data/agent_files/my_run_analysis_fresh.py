import stim

def count_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        n = len(instr.targets_copy())
        if instr.name in ['CX', 'CNOT']:
            cx_count += n // 2
            volume += n // 2
        elif instr.name in ['CZ', 'CY', 'SWAP']:
            # CZ, CY, SWAP count for volume but not CX
            volume += n // 2
        elif instr.name in ['H', 'S', 'S_DAG', 'SQRT_X', 'SQRT_X_DAG', 'SQRT_Y', 'SQRT_Y_DAG', 'X', 'Y', 'Z', 'I']:
            volume += n
    return cx_count, volume

def solve():
    # Load stabilizers
    with open('my_stabilizers_fresh.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    stabilizers = [stim.PauliString(s) for s in lines]
    
    # Load baseline
    with open('my_optimize_fresh.py', 'r') as f: # Wait, I named the stim file my_optimize_fresh.py by mistake in the previous create call!
        # It's actually a stim file content in a .py file? No, I put the content of stim in my_optimize_fresh.py
        # I need to read it as text.
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    base_cx, base_vol = count_metrics(baseline)
    print(f"Baseline: CX={base_cx}, Vol={base_vol}, Depth={len(baseline)}")

    # Verify baseline preserves stabilizers
    sim = stim.TableauSimulator()
    sim.do_circuit(baseline)
    preserved = 0
    for s in stabilizers:
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
    print(f"Baseline preserved: {preserved}/{len(stabilizers)}")

    # Synthesize
    print("Synthesizing graph state...")
    try:
        t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        cand = t.to_circuit("graph_state")
        cx, vol = count_metrics(cand)
        print(f"Candidate: CX={cx}, Vol={vol}, Depth={len(cand)}")
        
        # Verify candidate
        sim2 = stim.TableauSimulator()
        sim2.do_circuit(cand)
        pres2 = 0
        for s in stabilizers:
            if sim2.peek_observable_expectation(s) == 1:
                pres2 += 1
        print(f"Candidate preserved: {pres2}/{len(stabilizers)}")

        if pres2 == len(stabilizers):
            if cx < base_cx:
                print("SUCCESS: Candidate has strictly fewer CX.")
                with open('my_candidate_fresh.stim', 'w') as f:
                    f.write(str(cand))
            elif cx == base_cx and vol < base_vol:
                print("SUCCESS: Candidate has equal CX and strictly lower Volume.")
                with open('my_candidate_fresh.stim', 'w') as f:
                    f.write(str(cand))
            else:
                print("FAILURE: Candidate is not strictly better.")
        else:
            print("FAILURE: Candidate does not preserve all stabilizers.")

    except Exception as e:
        print(f"Error during synthesis: {e}")

if __name__ == "__main__":
    solve()
