import stim

def reformat():
    with open("circuit_135_solution.stim", "r") as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    new_circuit = stim.Circuit()
    
    for instruction in circuit:
        if instruction.name in ["CX", "H", "R", "M", "X", "Y", "Z", "MX", "MY", "MZ"]:
            # Split into pairs or singles
            targets = instruction.targets_copy()
            if instruction.name in ["CX", "CZ", "SWAP"]:
                # 2 qubit gates
                for i in range(0, len(targets), 2):
                    new_circuit.append(instruction.name, targets[i:i+2])
            else:
                # 1 qubit gates or measurement
                for t in targets:
                    new_circuit.append(instruction.name, [t])
        else:
            new_circuit.append(instruction)
            
    print(str(new_circuit))

if __name__ == "__main__":
    reformat()
