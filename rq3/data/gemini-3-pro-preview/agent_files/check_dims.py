import stim

with open("my_stabilizers.txt") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Number of stabilizers: {len(lines)}")
for i, line in enumerate(lines):
    if len(line) > 84:
        print(f"Stabilizer {i} has length {len(line)}")
        print(line)

with open("baseline_rq3.stim") as f:
    circuit = stim.Circuit(f.read())
print(f"Number of qubits in baseline: {circuit.num_qubits}")
