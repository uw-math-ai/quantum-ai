import stim

c = stim.Circuit.from_file(r'data\gemini-3-pro-preview\agent_files\circuit_155.stim')
# We want to decompose it or just print it such that lines are short.
# iterating instructions
with open(r'data\gemini-3-pro-preview\agent_files\circuit_formatted.stim', 'w') as f:
    for instruction in c:
        if instruction.name == "CX" and len(instruction.targets_copy()) > 6:
            # Split into pairs
            targets = instruction.targets_copy()
            for i in range(0, len(targets), 2):
                t1 = targets[i]
                t2 = targets[i+1]
                f.write(f"CX {t1.value} {t2.value}\n")
        elif instruction.name in ["H", "S", "X", "Y", "Z"] and len(instruction.targets_copy()) > 10:
             targets = instruction.targets_copy()
             for t in targets:
                 f.write(f"{instruction.name} {t.value}\n")
        else:
            f.write(str(instruction) + "\n")
