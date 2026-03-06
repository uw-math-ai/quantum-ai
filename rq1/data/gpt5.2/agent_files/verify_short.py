import stim

def verify_short():
    print("Reading circuit...")
    circuit = stim.Circuit.from_file("data/gemini-3-pro-preview/agent_files/circuit_75_short.stim")
    print(f"Circuit loaded. Qubits: {circuit.num_qubits}")
    
    print("Reading stabilizers...")
    with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    pauli_strings = [stim.PauliString(line) for line in lines]
    
    print("Simulating...")
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    print("Checking stabilizers...")
    all_good = True
    for i, p in enumerate(pauli_strings):
        expectation = sim.peek_observable_expectation(p)
        if expectation != 1:
            print(f"Failed stabilizer {i}: {lines[i]} (expectation {expectation})")
            all_good = False
            
    if all_good:
        print("Short circuit verified successfully!")
    else:
        print("Short circuit verification FAILED.")

if __name__ == "__main__":
    verify_short()
