import stim

def check_baseline():
    try:
        # Load baseline
        with open("baseline_task.stim", "r") as f:
            baseline = stim.Circuit(f.read())
            
        # Load target stabilizers
        with open("target_stabilizers_job_v7.txt", "r") as f:
            lines = [line.strip().replace(",", "") for line in f if line.strip()]
        
        target_stabilizers = [stim.PauliString(line) for line in lines]
        
        # Simulate baseline to get output state
        sim = stim.TableauSimulator()
        sim.do(baseline)
        
        # Check expectation of each stabilizer
        all_preserved = True
        for i, stab in enumerate(target_stabilizers):
            # peek_observable_expectation returns 1, -1, or 0 (uncertain)
            expect = sim.peek_observable_expectation(stab)
            if expect != 1:
                print(f"Stabilizer {i} not preserved. Expectation: {expect}")
                all_preserved = False
                
        if all_preserved:
            print("Baseline preserves all stabilizers.")
        else:
            print("Baseline does NOT preserve all stabilizers.")
            
        # Also check commutation in Python again just to be sure
        print("Checking commutation of first few...")
        for i in range(len(target_stabilizers)):
            for j in range(i+1, len(target_stabilizers)):
                if not target_stabilizers[i].commutes(target_stabilizers[j]):
                     print(f"Stabilizers {i} and {j} ANTICOMMUTE!")
                     return

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_baseline()
