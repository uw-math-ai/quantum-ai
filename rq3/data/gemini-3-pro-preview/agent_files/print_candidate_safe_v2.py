import stim

c = stim.Circuit.from_file("candidate.stim")
for instruction in c:
    name = instruction.name
    if name == "TICK":
        print("TICK")
        continue

    targets = instruction.targets_copy()
    
    if name in ["CZ", "CX"]:
        for i in range(0, len(targets), 2):
            print(f"{name} {targets[i].value} {targets[i+1].value}")
    elif name in ["H", "S", "X", "Y", "Z", "RX", "RY", "RZ", "I"]:
        for t in targets:
            print(f"{name} {t.value}")
    else:
        # Fallback for other gates
        print(instruction)
