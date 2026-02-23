import stim

def solve():
    # Read the circuit
    with open("circuit_49_generated.stim", "r") as f:
        circuit_str = f.read()
    
    # Read the stabilizers
    with open("stabilizers_49.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Number of stabilizers: {len(stabilizers)}")

    circuit = stim.Circuit(circuit_str)
    
    # Check if the circuit prepares a state that satisfies the stabilizers
    # We can do this by simulating the circuit and checking the expectation values of the stabilizers
    # Or by conjugating the stabilizers by the inverse of the circuit and checking if they map to +Z or +I or something trivial.
    # Actually, easier: initialize to |0>, apply circuit, measure stabilizers. They should be deterministic +1.
    
    # However, if the circuit is 49 qubits, and we have 48 stabilizers, it's fine.
    
    # Let's use Tableau simulator
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    all_good = True
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        # We want to check if the current state is a +1 eigenstate of s.
        # measure_expectation returns the expectation value. 
        # For a stabilizer state, it should be +1 or -1 (or 0 if not an eigenstate).
        # But we want it to be +1.
        
        # peek_observable_expectation(observable)
        ev = sim.peek_observable_expectation(s)
        if ev != 1:
            print(f"Stabilizer {s_str} not satisfied. Expectation: {ev}")
            all_good = False
            # break # Don't break, see how many fail
        
    if all_good:
        print("Verification successful: All stabilizers satisfied.")
    else:
        print("Verification failed.")

if __name__ == "__main__":
    solve()
