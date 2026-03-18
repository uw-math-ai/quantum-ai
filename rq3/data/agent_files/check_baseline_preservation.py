import stim
import sys

def check_stabilizers():
    with open("task_stabilizers.txt", "r") as f:
        stabs_text = f.read().strip()
    stabs = [s.strip() for s in stabs_text.split(",") if s.strip()]

    with open("task_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())

    # Simulate baseline
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    preserved = 0
    failed = []
    
    for i, s in enumerate(stabs):
        p = stim.PauliString(s)
        if sim.peek_observable_expectation(p) == 1:
            preserved += 1
        else:
            failed.append(i)
            
    print(f"Preserved: {preserved}/{len(stabs)}")
    if failed:
        print(f"Failed indices: {failed}")
        
    # Check anticommuting pair 42 and 45
    p42 = stim.PauliString(stabs[42])
    p45 = stim.PauliString(stabs[45])
    
    exp42 = sim.peek_observable_expectation(p42)
    exp45 = sim.peek_observable_expectation(p45)
    
    print(f"Expectation 42: {exp42}")
    print(f"Expectation 45: {exp45}")

if __name__ == "__main__":
    check_stabilizers()
