import stim
import sys

def verify():
    print("Loading files...")
    with open("current_task_stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    with open("candidate.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    print(f"Verifying circuit with {len(stabilizers)} stabilizers...")
    
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    failed = 0
    for i, s_str in enumerate(stabilizers):
        try:
            s = stim.PauliString(s_str)
            exp = sim.peek_observable_expectation(s)
            if exp != 1:
                print(f"Stabilizer {i} failed: {s_str} -> {exp}")
                failed += 1
        except Exception as e:
            print(f"Error checking stabilizer {i}: {e}")
            failed += 1
            
    if failed == 0:
        print("All stabilizers preserved!")
    else:
        print(f"Failed to preserve {failed} stabilizers.")
        sys.exit(1)

if __name__ == "__main__":
    verify()
