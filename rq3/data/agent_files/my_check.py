import stim

def check():
    try:
        with open("my_target_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
            stabilizers = [stim.PauliString(l) for l in lines]
            print(f"Loaded {len(stabilizers)} stabilizers.")
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    try:
        with open("my_baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
            print(f"Loaded baseline with {len(baseline)} instructions.")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    candidate = None
    try:
        with open("candidate.stim", "r") as f:
            candidate = stim.Circuit(f.read())
            print(f"Loaded candidate with {len(candidate)} instructions.")
    except Exception as e:
        print(f"Error loading candidate: {e}")

    # Check Baseline
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    failed_base = []
    for i, stab in enumerate(stabilizers):
        if sim.peek_observable_expectation(stab) != 1:
            failed_base.append(i)
            
    if failed_base:
        print(f"Baseline FAILS {len(failed_base)} stabilizers: {failed_base}")
    else:
        print("Baseline preserves all stabilizers.")

    # Check Candidate
    if candidate:
        sim = stim.TableauSimulator()
        sim.do(candidate)
        
        failed_cand = []
        for i, stab in enumerate(stabilizers):
            if sim.peek_observable_expectation(stab) != 1:
                failed_cand.append(i)
                
        if failed_cand:
            print(f"Candidate FAILS {len(failed_cand)} stabilizers: {failed_cand}")
            for i in failed_cand:
                print(f"  Failed {i}: {stabilizers[i]}")
        else:
            print("Candidate preserves all stabilizers.")

if __name__ == "__main__":
    check()
