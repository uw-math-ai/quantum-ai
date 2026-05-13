import stim

circuit = stim.Circuit.from_file("original.stim")
ops = []
for instr in circuit:
    if instr.name in ["CX", "SWAP", "CZ", "CY"]:
        targets = instr.targets_copy()
        for k in range(0, len(targets), 2):
            ops.append((instr.name, [targets[k].value, targets[k+1].value]))
    elif instr.name in ["H", "S", "X", "Y", "Z", "I"]:
        targets = instr.targets_copy()
        for t in targets:
            ops.append((instr.name, [t.value]))

print(f"Total ops: {len(ops)}")
target_indices = [214, 215, 216]
for idx in target_indices:
    if 0 <= idx < len(ops):
        print(f"Op {idx}: {ops[idx]}")

# Also find context
start = max(0, 210)
end = min(len(ops), 220)
print("\nContext:")
for i in range(start, end):
    print(f"{i}: {ops[i]}")
