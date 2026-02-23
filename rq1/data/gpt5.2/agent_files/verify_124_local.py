import stim
import sys

def verify():
    try:
        # Load circuit
        with open("circuit_124_attempt.stim", "r") as f:
            circuit_text = f.read()
        circuit = stim.Circuit(circuit_text)
        
        # Load stabilizers
        with open("data/stabilizers_124.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        stabilizers = [stim.PauliString(s) for s in lines]
        
        # Simulate
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        failures = 0
        for i, stab in enumerate(stabilizers):
            expectation = sim.peek_observable_expectation(stab)
            if expectation != 1:
                print(f"Stabilizer {i} failed: expectation {expectation}")
                failures += 1
        
        if failures == 0:
            print("SUCCESS: All stabilizers verified locally.")
        else:
            print(f"FAILURE: {failures} stabilizers failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during verification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
