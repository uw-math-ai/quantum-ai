import stim

try:
    with open("circuit.stim", "r") as f:
        content = f.read()
    c = stim.Circuit(content)
    print("Parsed successfully!")
    last_instr = c[-1]
    print(f"Last instruction: {last_instr}")
    targets = last_instr.targets_copy()
    print(f"Targets: {[t.value for t in targets]}")
    print(f"Count: {len(targets)}")
except Exception as e:
    print(f"Error parsing: {e}")
