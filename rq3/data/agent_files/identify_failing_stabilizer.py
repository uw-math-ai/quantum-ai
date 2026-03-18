import stim
import sys

def check():
    print("Reading files...")
    with open("target_stabilizers_task_v10.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    with open("baseline_task_v11.stim", "r") as f:
        baseline_text = f.read()
        
    circuit = stim.Circuit(baseline_text)
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    print("Checking stabilizers...")
    for i, stab in enumerate(stabilizers):
        try:
            p = stim.PauliString(stab)
            if sim.peek_observable_expectation(p) != 1:
                print(f"FAIL: Stabilizer {i} not preserved (expectation {sim.peek_observable_expectation(p)})")
                # Check anticommutation with others?
                # No need, just identify it.
        except Exception as e:
            print(f"Error checking stabilizer {i}: {e}")

if __name__ == "__main__":
    check()
