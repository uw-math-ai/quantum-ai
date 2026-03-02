import stim

def reformat_circuit():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_133.stim', 'r') as f:
        circuit = stim.Circuit(f.read())
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name in ["CX", "CNOT"]:
            targets = instruction.targets_copy()
            # Process in pairs
            for i in range(0, len(targets), 2):
                new_circuit.append(instruction.name, targets[i:i+2])
        elif instruction.name in ["H", "X", "Y", "Z", "I"]:
            targets = instruction.targets_copy()
            # Process individually or in small chunks
            for t in targets:
                new_circuit.append(instruction.name, [t])
        else:
            # Other gates (like M, R, etc.), just copy for now (assuming they aren't massive)
            new_circuit.append(instruction)
            
    # Save to file
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_clean.stim', 'w') as f:
        for instruction in new_circuit:
            f.write(str(instruction) + "\n")
    print("Saved clean circuit to circuit_clean.stim")

if __name__ == '__main__':
    reformat_circuit()
