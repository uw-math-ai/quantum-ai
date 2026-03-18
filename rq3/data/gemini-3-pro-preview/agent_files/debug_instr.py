import stim

with open("candidate_1_split.stim") as f:
    c = stim.Circuit(f.read())

print("Instructions in candidate_1_split.stim:")
for instr in c:
    print(f"{instr.name} targets={len(instr.targets_copy())}")
