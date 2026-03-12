import stim

def check():
    print("Loading circuits...")
    with open('current_task_baseline.stim', 'r') as f:
        base = stim.Circuit(f.read())
    with open('candidate.stim', 'r') as f:
        cand = stim.Circuit(f.read())
    
    # Simulate
    sim_base = stim.TableauSimulator()
    sim_base.do(base)
    tab_base = sim_base.current_inverse_tableau().inverse()
    
    sim_cand = stim.TableauSimulator()
    sim_cand.do(cand)
    tab_cand = sim_cand.current_inverse_tableau().inverse()
    
    print(f"Base == Cand: {tab_base == tab_cand}")
    
    if tab_base != tab_cand:
        print("Tableaus differ.")
        # Check stabilizers
        stabs = sim_base.canonical_stabilizers()
        preserved = 0
        total = 0
        for s in stabs:
            total += 1
            if sim_cand.peek_observable_expectation(s) == 1:
                preserved += 1
        print(f"Preserved {preserved}/{total} stabilizers.")

if __name__ == "__main__":
    check()
