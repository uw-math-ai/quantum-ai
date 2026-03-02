import stim

def verify():
    # Load circuit
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\circuit_92_final.stim", "r") as f:
        circuit_text = f.read()
    
    circuit = stim.Circuit(circuit_text)
    
    # Load ORIGINAL stabilizers (with the typo)
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\stabilizers_92.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    # We expect it to FAIL on the original bad stabilizer (index 16)
    # But pass on all others.
    
    # Let's verify this expectation.
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check each stabilizer
    results = []
    for i, s in enumerate(stabilizers):
        p = stim.PauliString(s)
        # Measure expectation value
        # Since it's a stabilizer state, expectation should be +1 or -1.
        # check_observable returns True if expectation is -1? No.
        # peek_observable_expectation returns +1 or -1.
        
        # actually, measure_expectation is better
        # expectation = sim.peek_observable_expectation(p)
        # But wait, we can just use `measure_expectation`?
        # No, `peek_observable_expectation` is what we want.
        
        # If the state is a stabilizer state, the expectation is +/- 1.
        # Unless it's 0 (anticommutes with current stabilizers).
        
        # However, `peek_observable_expectation` might be slow if many qubits?
        # No, it's efficient for stabilizer states.
        
        expect = sim.peek_observable_expectation(p)
        if expect == 1:
            results.append(True)
        else:
            results.append(False)
            print(f"Failed stabilizer {i}: {s} (expect={expect})")
            
    success_count = sum(results)
    print(f"Satisfied {success_count}/{len(stabilizers)} stabilizers.")
    
    if success_count == len(stabilizers) - 1:
        print("As expected, all but one satisfied.")
    elif success_count == len(stabilizers):
        print("Wow, all satisfied? That would mean the original set didn't anticommute?")
    else:
        print("More failures than expected.")

if __name__ == "__main__":
    verify()
