import stim

def main():
    with open("data/agent_files/best_candidate_optimized.stim", "r") as f:
        c = stim.Circuit(f.read())
    
    with open("data/agent_files/candidate_formatted.stim", "w") as f:
        for instr in c:
            if instr.name == "CX":
                targets = instr.targets_copy()
                for i in range(0, len(targets), 2):
                    f.write(f"CX {targets[i].value} {targets[i+1].value}\n")
            elif instr.name == "H":
                targets = instr.targets_copy()
                for t in targets:
                    f.write(f"H {t.value}\n")
            else:
                f.write(str(instr) + "\n")

if __name__ == "__main__":
    main()
