import stim

try:
    with open("candidate_graph_baseline.stim") as f:
        circuit = stim.Circuit(f.read())
except Exception as e:
    print(f"Error loading candidate: {e}")
    exit(1)

new_circuit = stim.Circuit()
for op in circuit:
    if op.name == "CZ":
        # Decompose CZ targets[0], targets[1] -> H targets[1], CX targets[0] targets[1], H targets[1]
        # CZ is symmetric, so target choice doesn't matter for logic, but might for optimization.
        # We can just pick the second as target.
        targets = op.targets_copy()
        # CZ can have multiple targets: CZ 0 1 2 3 ... means CZ 0 1, CZ 2 3 ...
        for i in range(0, len(targets), 2):
            q1 = targets[i].value
            q2 = targets[i+1].value
            new_circuit.append("H", [q2])
            new_circuit.append("CX", [q1, q2])
            new_circuit.append("H", [q2])
    else:
        new_circuit.append(op)

with open("candidate_decomposed.stim", "w") as f:
    f.write(str(new_circuit))

print("Candidate saved to candidate_decomposed.stim")
