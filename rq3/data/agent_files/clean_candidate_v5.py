import stim

c = stim.Circuit.from_file("candidate.stim")

with open("candidate_clean.stim", "w") as f:
    for inst in c:
        if inst.name == "CZ" and len(inst.targets_copy()) > 10:
            targets = inst.targets_copy()
            # Process in pairs
            for i in range(0, len(targets), 2):
                f.write(f"CZ {targets[i].value} {targets[i+1].value}\n")
        elif inst.name in ["H", "S", "X", "Y", "Z"] and len(inst.targets_copy()) > 10:
             targets = inst.targets_copy()
             for t in targets:
                 f.write(f"{inst.name} {t.value}\n")
        else:
            f.write(str(inst) + "\n")
