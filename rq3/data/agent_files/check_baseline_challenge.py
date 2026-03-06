import stim
import sys

def check():
    # Load stabilizers
    with open('target_stabilizers_challenge.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    # Load baseline
    with open('baseline_challenge.stim', 'r') as f:
        baseline_text = f.read()
    
    circuit = stim.Circuit(baseline_text)
    
    # Simulate
    # Need to verify +1 or -1
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    failed = []
    
    for i, s_str in enumerate(stabilizers):
        try:
            s = stim.PauliString(s_str)
            # measurement result is 0 for +1, 1 for -1. Wait, let's verify.
            # measure_observable returns the measurement outcome (0 or 1).
            # If +1 eigenvalue, measurement is 0 (with probability 1).
            # If -1 eigenvalue, measurement is 1 (with probability 1).
            # If indefinite, measurement is random (0 or 1).
            res = sim.peek_observable_expectation(s)
            if res == 1:
                preserved += 1
            else:
                failed.append(i)
        except Exception as e:
            print(f"Error checking stabilizer {i}: {e}")
            
    print(f"Baseline preserves {preserved}/{len(stabilizers)} stabilizers.")
    if failed:
        print(f"Failed indices: {failed}")

if __name__ == "__main__":
    check()
