import stim

def verify_baseline_prompt():
    with open("current_task_baseline.stim", "r") as f:
        baseline = stim.Circuit(f.read())
        
    with open("target_stabilizers_prompt.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
        
    print(f"Loaded {len(lines)} stabilizers from prompt file.")
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    success = True
    for i, s_str in enumerate(lines):
        # Determine expected length
        # Assuming stabilizer string corresponds to qubits 0..len-1
        # But baseline has 133 qubits.
        # If string is shorter, we pad with I?
        # Or does PauliString handle it?
        
        # stim.PauliString(s_str) creates a PauliString of length len(s_str).
        # If we pass it to peek_observable_expectation, it checks against the first len(s_str) qubits.
        # This assumes the prompt stabilizers are for 0..118.
        
        try:
            p = stim.PauliString(s_str)
            # Check expectation
            ev = sim.peek_observable_expectation(p)
            if ev != 1:
                print(f"FAIL: Stabilizer {i} expected +1, got {ev}")
                success = False
                break
        except Exception as e:
            print(f"ERROR on stabilizer {i}: {e}")
            success = False
            break
            
    if success:
        print("SUCCESS: Baseline preserves all prompt stabilizers.")
    else:
        print("FAILURE: Baseline does not preserve prompt stabilizers.")

if __name__ == "__main__":
    verify_baseline_prompt()
