import stim

def main():
    with open("candidate_formatted.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "CZ":
            targets = instr.targets_copy()
            # Split into pairs
            for i in range(0, len(targets), 2):
                new_circuit.append("CZ", targets[i:i+2])
        elif instr.name == "H":
             targets = instr.targets_copy()
             # Split into single
             for t in targets:
                 new_circuit.append("H", [t])
        else:
            new_circuit.append(instr)
            
    with open("candidate_split.stim", "w") as f:
        f.write(str(new_circuit))
        
if __name__ == "__main__":
    main()
