import stim
import sys

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        content = f.read()
    stabilizers = [s.strip() for s in content.replace('\n', '').split(',') if s.strip()]
    return stabilizers

def check():
    stabilizers = read_stabilizers("target_stabilizers_prompt.txt")
    
    with open("candidate.stim", "r") as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    
    # Simulate the circuit to get the tableau
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    failed_count = 0
    for i, s_str in enumerate(stabilizers):
        s = stim.PauliString(s_str)
        # peek_observable_expectation returns +1, -1, or 0
        expectation = sim.peek_observable_expectation(s)
        if expectation != 1:
            print(f"Stabilizer {i} failed: {s_str} (Expectation: {expectation})")
            failed_count += 1
            if failed_count > 10:
                print("... (stopping after 10 failures)")
                break
    
    print(f"Total failed: {failed_count} out of {len(stabilizers)}")

if __name__ == "__main__":
    check()
