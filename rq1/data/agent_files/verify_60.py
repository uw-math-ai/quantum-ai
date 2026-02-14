import stim

def verify():
    print("Reading stabilizers...")
    with open('target_stabilizers_60.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    pauli_strings = [stim.PauliString(line) for line in lines]

    print("Reading circuit...")
    with open('circuit_attempt.stim', 'r') as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)

    print("Simulating...")
    sim = stim.TableauSimulator()
    sim.do(circuit)

    print("Checking stabilizers...")
    failed = 0
    for i, p in enumerate(pauli_strings):
        expectation = sim.peek_observable_expectation(p)
        if expectation != 1:
            print(f"Stabilizer {i} failed: {p}, expectation: {expectation}")
            failed += 1
            
    if failed == 0:
        print("LOCAL VERIFICATION: SUCCESS")
    else:
        print(f"LOCAL VERIFICATION: FAILED ({failed} failures)")

if __name__ == "__main__":
    verify()
