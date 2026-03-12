import stim

def split_circuit():
    with open('candidate.stim', 'r') as f:
        c = stim.Circuit(f.read())
    
    out_lines = []
    
    for instr in c:
        name = instr.name
        targets = instr.targets_copy()
        args = instr.gate_args_copy()
        
        # Gates like TICK or empty targets
        if not targets:
            # Reconstruct string for simple instruction
            s = str(instr)
            out_lines.append(s)
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
        
        # Build argument string if needed
        arg_str = ""
        if args:
            arg_str = "(" + ",".join(str(a) for a in args) + ")"
            
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            if not chunk: continue
            
            # Construct line manually
            line = name + arg_str
            for t in chunk:
                line += " " + str(t.value) # assuming simple targets
            out_lines.append(line)
            
    # Join with newlines
    result = "\n".join(out_lines)
    
    with open('candidate_split.stim', 'w') as f:
        f.write(result)
        
    print(result)

if __name__ == "__main__":
    split_circuit()
