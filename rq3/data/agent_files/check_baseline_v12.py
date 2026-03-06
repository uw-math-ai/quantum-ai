import stim
import sys

def check():
    print("Reading files...")
    with open("target_stabilizers_task_v10.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    with open("baseline_task_v11.stim", "r") as f:
        baseline_text = f.read()
        
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    circuit = stim.Circuit(baseline_text)
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    failed = 0
    for i, stab in enumerate(stabilizers):
        try:
            p = stim.PauliString(stab)
            if sim.peek_observable_expectation(p) == 1:
                preserved += 1
            else:
                # print(f"Baseline fails stabilizer {i}")
                failed += 1
        except Exception as e:
            print(f"Error checking stabilizer {i}: {e}")
            failed += 1
            
    print(f"Baseline preserved: {preserved}/{len(stabilizers)}")
    print(f"Baseline failed: {failed}")

if __name__ == "__main__":
    check()
