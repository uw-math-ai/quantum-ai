import stim

def reformat():
    with open(r'data\gemini-3-pro-preview\agent_files\circuit_125.stim', 'r') as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    new_circuit = stim.Circuit()
    for instruction in circuit:
        targets = instruction.targets_copy()
        args = instruction.gate_args_copy()
        name = instruction.name
        
        # Split long instructions. CX has pairs, so step must be even.
        step = 10
        if name == "CX" or name == "CNOT" or name == "CZ" or name == "SWAP":
            step = 10 # 5 pairs
        
        if len(targets) > step and not args: 
             for i in range(0, len(targets), step):
                 new_circuit.append(name, targets[i:i+step], args)
        else:
            new_circuit.append(name, targets, args)
            
    print(new_circuit)

if __name__ == "__main__":
    reformat()
