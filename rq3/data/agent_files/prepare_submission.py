import stim

def main():
    with open("data/agent_files/candidate.stim", "r") as f:
        circ = stim.Circuit(f.read())
    
    new_circ = stim.Circuit()
    for instruction in circ:
        name = instruction.name
        targets = instruction.targets_copy()
        
        if name == "RX":
            # RX resets to |+>. From |0>, H does this.
            new_circ.append("H", targets)
        elif name in ["R", "RZ"]:
            # R resets to |0>. From |0>, this is Identity.
            pass
        elif name == "RY":
            # RY resets to |i+>. From |0>, H then S does this.
            new_circ.append("H", targets)
            new_circ.append("S", targets)
        else:
            new_circ.append(instruction)
            
    with open("data/agent_files/candidate.stim", "w") as f:
        f.write(str(new_circ))
        
if __name__ == "__main__":
    main()
