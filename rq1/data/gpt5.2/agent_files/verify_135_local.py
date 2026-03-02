import stim
import sys
import json

import hashlib

def verify_local():
    try:
        # Load stabilizers
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_135.txt", 'r') as f:
            stabilizers = [line.strip() for line in f if line.strip()]

        print(f"Stabilizers hash: {hashlib.sha256(json.dumps(stabilizers).encode()).hexdigest()}")

        # Load circuit
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_135.stim", 'r') as f:
            circuit_str = f.read()

        print(f"Circuit hash: {hashlib.sha256(circuit_str.encode()).hexdigest()}")
        
        c = stim.Circuit(circuit_str)
        
        # Verify
        # We can simulate the circuit and check if the stabilizers are preserved.
        # But we want to check if the prepared state is a +1 eigenstate.
        
        # Method 1: Tableau simulation
        sim = stim.TableauSimulator()
        sim.do(c)
        
        results = {}
        preserved = 0
        total = 0
        
        for s in stabilizers:
            # Measure the stabilizer expectation value
            # If the state is stabilized by S, expectation should be +1.
            # measure_observable expects a Pauli string.
            # We can peek at the expectation value.
            # check_observable returns True if the observable is +1, False if -1.
            # Wait, stim.TableauSimulator.measure_expectation is not available?
            # We can use peek_observable_expectation(observables) -> result
            
            p = stim.PauliString(s)
            expectation = sim.peek_observable_expectation(p)
            
            is_preserved = (expectation == 1)
            results[s] = is_preserved
            if is_preserved:
                preserved += 1
            total += 1
            
        print(f"Preserved: {preserved}/{total}")
        
        if preserved < total:
            print("Some stabilizers are not preserved.")
            # print(results)
        else:
            print("All stabilizers preserved.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_local()
