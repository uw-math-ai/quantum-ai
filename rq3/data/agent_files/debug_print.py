import stim

def debug():
    with open('candidate.stim', 'r') as f:
        c = stim.Circuit(f.read())
    
    for instruction in c:
        if instruction.name == "H":
            print(f"Instruction: {instruction.name}, Targets: {len(instruction.targets_copy())}")
            break

if __name__ == "__main__":
    debug()
