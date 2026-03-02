import stim

def verify():
    # Read circuit
    with open("circuit_119_new.stim", "r") as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    # Read stabilizers
    with open("stabilizers_119.txt", "r") as f:
        stabilizers = [l.strip() for l in f if l.strip()]

    print(f"Verifying {len(stabilizers)} stabilizers on {circuit.num_qubits} qubits...")

    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    failed = 0
    for i, s_str in enumerate(stabilizers):
        s = stim.PauliString(s_str)
        expectation = sim.peek_observable_expectation(s)
        if expectation != 1:
            print(f"Stabilizer {i} failed: expectation {expectation}")
            failed += 1
            
    if failed == 0:
        print("All stabilizers verified successfully!")
    else:
        print(f"Failed {failed} stabilizers.")

if __name__ == "__main__":
    verify()
