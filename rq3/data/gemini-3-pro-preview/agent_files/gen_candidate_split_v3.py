import stim

def split_circuit():
    with open('candidate.stim', 'r') as f:
        c = stim.Circuit(f.read())
    
    new_c = stim.Circuit()
    for instr in c:
        name = instr.name
        targets = instr.targets_copy()
        args = instr.gate_args_copy()
        
        # Gates like TICK or empty targets
        if not targets:
            new_c.append(instr)
            continue
            
        # Determine arity for chunking
        arity = 1
        if name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "CNOT"]:
            arity = 2
        elif name in ["CCZ", "CCX", "CCY"]:
            arity = 3
        
        # Chunk size in terms of target count
        # 10 * arity ~ 20 targets ~ 60-80 chars.
        chunk_size = 10 * arity
        
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            if not chunk: continue
            new_c.append(name, chunk, args)
            
    with open('candidate_split.stim', 'w') as f:
        f.write(str(new_c))
        
    print(str(new_c))

if __name__ == "__main__":
    split_circuit()
