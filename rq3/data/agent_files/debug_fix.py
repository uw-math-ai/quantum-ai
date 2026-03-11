import stim

with open("candidate.stim") as f:
    circ = stim.Circuit(f.read())

print(f"Loaded circuit with {len(circ)} instructions")
for op in circ:
    print(f"Op: {repr(op.name)}, targets: {len(op.targets_copy())}")

new_circ = stim.Circuit()
for op in circ:
    if op.name == "CZ":
        print("Processing CZ")
        targets = op.targets_copy()
        for i in range(0, len(targets), 2):
            new_circ.append("CZ", [targets[i], targets[i+1]])
    elif op.name in ["H", "S", "X", "Z", "Y"]:
        print(f"Processing {op.name}")
        targets = op.targets_copy()
        for t in targets:
            new_circ.append(op.name, [t])
    else:
        print(f"Skipping {op.name} (else branch)")
        new_circ.append(op)

print(f"New circuit has {len(new_circ)} instructions")

with open("candidate_fixed.stim", "w") as f:
    for op in new_circ:
        print(str(op), file=f)
