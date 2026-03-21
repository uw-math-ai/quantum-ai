
import stim
import sys

def load_file(path):
    with open(path, 'r') as f:
        return f.read().strip()

try:
    circuit_str = load_file("data/gemini-3-pro-preview/agent_files_ft/circuit.stim")
    stabilizers_str = load_file("data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt")
except FileNotFoundError:
    circuit_str = load_file("data/gemini-3-pro-preview/agent_files_ft/circuit.stim")
    stabilizers_str = load_file("data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt")

circuit = stim.Circuit(circuit_str)
stabilizers = [stim.PauliString(s.strip()) for s in stabilizers_str.split(',') if s.strip()]

sim = stim.TableauSimulator()
sim.do(circuit)

failed_indices = []
for i, s in enumerate(stabilizers):
    exp = sim.peek_observable_expectation(s)
    if exp != 1:
        failed_indices.append(i)
        print(f"Stabilizer {i} failed (expectation {exp})")
        # print support
        indices = [k for k in range(len(s)) if s[k] != 0]
        print(f"Support: {indices}")
        print(f"Paulis: {[s[k] for k in indices]}")

print(f"Total failures: {len(failed_indices)}")
