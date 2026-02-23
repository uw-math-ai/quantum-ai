import stim

def verify():
    # Load circuit
    with open('circuit_generated.stim', 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    # Load stabilizers
    with open('stabilizers_148.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    # Check
    print("Simulating...")
    tableau = circuit.to_tableau()
    
    failed = 0
    for i, line in enumerate(lines):
        # Check if tableau stabilizes this
        # tableau(Z_k) is the stabilizer of k-th qubit in the tableau?
        # No. tableau represents the Clifford operation.
        # We need to apply the inverse tableau to the stabilizer and see if it maps to +Z or -Z on some qubit?
        # No. The circuit prepares a state |psi>.
        # We want P |psi> = |psi>.
        # So <psi| P |psi> = 1.
        # We can use tableau simulator.
        
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        # Check expectation value
        pauli = stim.PauliString(line)
        expectation = sim.peek_observable_expectation(pauli)
        
        if expectation != 1:
            print(f"Stabilizer {i} failed: expectation {expectation}")
            failed += 1
            
    if failed == 0:
        print("All stabilizers verified locally!")
    else:
        print(f"Failed {failed} stabilizers.")

verify()
