import stim

with open("circuit_attempt.stim", "r") as f:
    circuit = stim.Circuit(f.read())

for instruction in circuit:
    name = instruction.name
    targets = instruction.targets_copy()
    args = instruction.gate_args_copy()
    
    if args:
        # If there are args, just print it as is (usually simple)
        print(instruction)
    else:
        # Chunk targets
        chunk_size = 10
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            t_str = " ".join(str(t).replace("stim.GateTarget(", "").replace(")", "") for t in chunk)
            # stim.GateTarget representation is weird in str?
            # actually t.value gives the qubit index if it's a qubit
            
            # Let's use circuit.append logic to reconstruct string
            # Or just print carefully
            
            # Better: create a temporary circuit with just this chunk and print it
            temp = stim.Circuit()
            temp.append(name, chunk, args)
            print(str(temp).strip())
