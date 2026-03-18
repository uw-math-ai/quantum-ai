
import stim

def main():
    try:
        # Load baseline
        with open("current_baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        # Load stabilizers
        with open("current_target_stabilizers.txt", "r") as f:
            stabilizer_lines = [line.strip() for line in f if line.strip()]
        stabilizers = [stim.PauliString(s) for s in stabilizer_lines]
        
        print(f"Checking {len(stabilizers)} stabilizers against baseline.")
        
        sim = stim.TableauSimulator()
        sim.do(baseline)
        
        correct = 0
        for s in stabilizers:
            if sim.peek_observable_expectation(s) == 1:
                correct += 1
                
        print(f"Baseline preserves {correct}/{len(stabilizers)} stabilizers.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
