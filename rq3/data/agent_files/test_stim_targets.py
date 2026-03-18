import stim
def check():
    c = stim.Circuit("CZ 0 1 2 3")
    instr = c[0]
    targets = instr.targets_copy()
    print(f"Targets: {targets}")
    print(f"Target 0 type: {type(targets[0])}")
    print(f"Target 0 value: {targets[0].value}")

if __name__ == "__main__":
    check()
