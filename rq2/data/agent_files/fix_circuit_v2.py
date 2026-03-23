import stim

def main():
    try:
        with open("candidate.stim", "r") as f:
            c = stim.Circuit(f.read())
    except Exception as e:
        print(f"Error reading candidate.stim: {e}")
        return

    try:
        with open("candidate_fixed_v2.stim", "w") as f:
            for inst in c:
                if inst.name == "CX":
                    targets = inst.targets_copy()
                    if len(targets) > 2:
                        # Split
                        for k in range(0, len(targets), 2):
                            # Ensure we don't go out of bounds? Stim guarantees pairs for CX.
                            print(f"CX {targets[k].value} {targets[k+1].value}", file=f)
                    else:
                        print(f"CX {targets[0].value} {targets[1].value}", file=f)
                elif inst.name == "M":
                     targets = inst.targets_copy()
                     for t in targets:
                         print(f"M {t.value}", file=f)
                elif inst.name == "H":
                     targets = inst.targets_copy()
                     for t in targets:
                         print(f"H {t.value}", file=f)
                else:
                    print(str(inst), file=f)
        print("Success: candidate_fixed_v2.stim created")
    except Exception as e:
        print(f"Error writing: {e}")

if __name__ == "__main__":
    main()
