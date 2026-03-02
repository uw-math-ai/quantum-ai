import stim
import sys

def verify():
    # Load stabilizers
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186_clean.txt', 'r') as f:
        target_stabilizers = [line.strip() for line in f if line.strip()]

    # Load circuit
    with open(r'data/gemini-3-pro-preview/agent_files/circuit_186_subset.stim', 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)

    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    passed = 0
    failed = []
    for i, s in enumerate(target_stabilizers):
        p = stim.PauliString(s)
        expectation = sim.peek_observable_expectation(p)
        if expectation == 1:
            passed += 1
        else:
            failed.append(i)

    print(f"Passed: {passed}/{len(target_stabilizers)}")
    if failed:
        print(f"Failed indices: {failed}")

if __name__ == "__main__":
    verify()
