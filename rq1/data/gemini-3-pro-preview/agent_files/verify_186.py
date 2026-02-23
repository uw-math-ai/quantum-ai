import stim
import sys

def verify():
    # Load stabilizers
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186_clean.txt', 'r') as f:
        target_stabilizers = [line.strip() for line in f if line.strip()]

    # Load circuit
    with open(r'data/gemini-3-pro-preview/agent_files/circuit_186.stim', 'r') as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)

    # Get the tableau of the circuit
    # The circuit prepares the state from |0...0>
    # So the stabilizers of the state are the rows of the tableau *after* the circuit
    # applied to the initial Z stabilizers.
    # Actually simpler: simulate the circuit on the tableau.
    
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    # Check each target stabilizer
    # A stabilizer S is stabilized if S * |psi> = |psi>
    # The state |psi> is stabilized by the tableau rows.
    # We can check if S is a linear combination of the tableau rows (Z output rows).
    # Or we can check if <psi|S|psi> = 1.
    # stim.TableauSimulator.measure_expectation can do this!
    
    failed = []
    for i, s in enumerate(target_stabilizers):
        p = stim.PauliString(s)
        expectation = sim.peek_observable_expectation(p)
        if expectation != 1:
            failed.append(i)
            # print(f"Stabilizer {i} failed: expectation {expectation}")

    if not failed:
        print("ALL STABILIZERS PRESERVED!")
    else:
        print(f"FAILED: {len(failed)} stabilizers not preserved.")
        print(f"Failed indices: {failed[:10]}...")

if __name__ == "__main__":
    verify()
