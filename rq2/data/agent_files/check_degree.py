import stim
import collections

circuit = stim.Circuit.from_file("original.stim")

control_counts = collections.defaultdict(int)
target_counts = collections.defaultdict(int)

# Flatten
ops = []
for instr in circuit:
    if instr.name in ["CX", "CNOT", "CZ", "CY"]:
        targets = instr.targets_copy()
        for k in range(0, len(targets), 2):
            c = targets[k].value
            t = targets[k+1].value
            control_counts[c] += 1
            target_counts[t] += 1
    elif instr.name in ["H", "S", "X", "Y", "Z"]:
        pass

print("High degree controls (> 7):")
for q, count in sorted(control_counts.items()):
    if count > 7:
        print(f"Qubit {q}: {count} controls")

print("\nHigh degree targets (> 7):")
for q, count in sorted(target_counts.items()):
    if count > 7:
        print(f"Qubit {q}: {count} targets")
