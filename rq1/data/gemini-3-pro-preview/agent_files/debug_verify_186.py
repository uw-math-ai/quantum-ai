import stim
import sys

def verify():
    # Load stabilizers
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186_clean.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Load circuit
    with open(r'data/gemini-3-pro-preview/agent_files/circuit_186.stim', 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)

    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    # Check the first stabilizer
    s = stabilizers[0]
    p = stim.PauliString(s)
    exp = sim.peek_observable_expectation(p)
    print(f"Stabilizer 0: {s}")
    print(f"Expectation: {exp}")

    # Check the last stabilizer
    s = stabilizers[-1]
    p = stim.PauliString(s)
    exp = sim.peek_observable_expectation(p)
    print(f"Stabilizer -1: {s}")
    print(f"Expectation: {exp}")

if __name__ == "__main__":
    verify()
