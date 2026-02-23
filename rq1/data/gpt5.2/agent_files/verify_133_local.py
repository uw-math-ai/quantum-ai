import stim
import sys

def verify_circuit():
    try:
        with open("circuit_133.stim", "r") as f:
            circuit_text = f.read()
        circuit = stim.Circuit(circuit_text)
    except Exception as e:
        print(f"Failed to load circuit: {e}")
        return

    try:
        with open("stabilizers_133.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Failed to load stabilizers: {e}")
        return

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    tableau_sim = stim.TableauSimulator()
    tableau_sim.do(circuit)
    
    failed = 0
    for i, s_str in enumerate(stabilizers):
        s = stim.PauliString(s_str)
        expectation = tableau_sim.peek_observable_expectation(s)
        
        if expectation != 1:
            print(f"Stabilizer {i} failed: {s_str}")
            print(f"Expectation: {expectation}")
            failed += 1
            if failed > 10:
                print("Too many failures, stopping.")
                break
    
    if failed == 0:
        print("SUCCESS: All stabilizers preserved.")
    else:
        print(f"FAILURE: {failed} stabilizers not preserved.")

if __name__ == "__main__":
    verify_circuit()
