import stim
import sys

def analyze_failure():
    try:
        with open("target_stabilizers_102.txt", "r") as f:
            target_stabilizers = [line.strip() for line in f if line.strip()]

        with open("circuit_102.stim", "r") as f:
            circuit_str = f.read()
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    circuit = stim.Circuit(circuit_str)
    
    # Simulate the circuit to get the final state stabilizer tableau
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    print(f"Checking {len(target_stabilizers)} stabilizers...")
    failures = []
    
    for i, s_str in enumerate(target_stabilizers):
        s = stim.PauliString(s_str)
        # Check if the state is stabilized by s
        # Stim: False -> 0 -> +1 eigenvalue
        #       True  -> 1 -> -1 eigenvalue
        # We want +1 eigenvalue, so we expect False.
        expect = sim.measure_observable(s)
        
        if expect: # If True (1), it failed (anticommuting)
            print(f"Stabilizer {i} failed: Outcome {expect} (-1 eigenvalue)")
            failures.append((i, s_str, expect))
            
    print(f"Total failed: {len(failures)}")
    if failures:
        print("First failure details:")
        print(failures[0])

if __name__ == "__main__":
    analyze_failure()
