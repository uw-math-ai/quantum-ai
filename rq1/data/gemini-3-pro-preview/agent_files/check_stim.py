import stim
try:
    c = stim.Circuit("H 0 1")
    instr = c[0]
    print(f"Instruction: {instr}")
    targets = instr.targets_copy()
    print(f"Targets: {targets}")
    c2 = stim.Circuit()
    c2.append("H", targets)
    print(f"Reconstructed: {c2}")
except Exception as e:
    print(f"Error: {e}")
