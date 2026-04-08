import stim

def print_around(filename, index, context=5):
    c = stim.Circuit(open(filename).read())
    ops = []
    for instr in c:
        if instr.name in ["CX", "SWAP", "CZ", "CY"]:
            targets = instr.targets_copy()
            for k in range(0, len(targets), 2):
                ops.append((instr.name, [targets[k].value, targets[k+1].value]))
        elif instr.name in ["H", "S", "X", "Y", "Z", "I"]:
            targets = instr.targets_copy()
            for t in targets:
                ops.append((instr.name, [t.value]))
                
    start = max(0, index - context)
    end = min(len(ops), index + context + 1)
    
    for i in range(start, end):
        prefix = ">> " if i == index else "   "
        print(f"{prefix}{i}: {ops[i]}")

print_around("original.stim", 812, 10)
