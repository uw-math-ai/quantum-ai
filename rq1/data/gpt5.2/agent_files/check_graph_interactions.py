import stim

with open("circuit_54_graph.stim", "r") as f:
    circuit = stim.Circuit(f.read())

print(f"Num qubits: {circuit.num_qubits}")

usage = {}
for i, instr in enumerate(circuit):
    for target in instr.targets_copy():
        if target.value > 53:
            if target.value not in usage:
                usage[target.value] = []
            usage[target.value].append(instr.name)
            
print(f"Usage > 53: {usage}")

# Check interactions
# If CZ involves >53 and <=53, then entangled.
interactions = []
for instr in circuit:
    if instr.name == "CZ":
        targets = [t.value for t in instr.targets_copy()]
        # CZ takes pairs
        for k in range(0, len(targets), 2):
            q1 = targets[k]
            q2 = targets[k+1]
            if (q1 > 53 and q2 <= 53) or (q2 > 53 and q1 <= 53):
                interactions.append((q1, q2))

print(f"Interactions with ancillas: {interactions}")
