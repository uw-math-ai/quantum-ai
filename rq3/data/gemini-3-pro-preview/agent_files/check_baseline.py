import stim

def check_baseline():
    with open("baseline_provided.stim", "r") as f:
        baseline = stim.Circuit(f.read())
    
    with open("target_stabilizers.txt", "r") as f:
        target_stabilizers = [stim.PauliString(line.strip()) for line in f if line.strip()]

    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    consistent = True
    for i, stab in enumerate(target_stabilizers):
        if sim.peek_observable_expectation(stab) != 1:
            print(f"Baseline fails to preserve stabilizer {i}: {stab}")
            consistent = False
            
    if consistent:
        print("Baseline preserves all target stabilizers.")
    else:
        print("Baseline does NOT preserve all target stabilizers.")

if __name__ == "__main__":
    check_baseline()
