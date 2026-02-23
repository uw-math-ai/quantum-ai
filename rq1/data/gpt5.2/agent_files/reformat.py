import stim

print("Reading circuit_generated.stim...")
with open("circuit_generated.stim", "r") as f:
    circuit = stim.Circuit(f.read())

safe_lines = []

for instruction in circuit:
    name = instruction.name
    targets = instruction.targets_copy()
    
    arity = 1
    if name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP", "CY", "ZC", "YC"]:
        arity = 2
    elif name in ["CCZ", "CCX", "Tof", "Toffoli"]:
        arity = 3
    elif name in ["MPP"]:
        arity = 0 # special handling
    
    if arity == 0:
        # Just use str(instruction) and hope it's not too long?
        # MPP is unlikely in elimination circuit.
        safe_lines.append(str(instruction))
        continue

    args = []
    for t in targets:
        args.append(str(t.value))
        
    # Group args
    if arity == 2:
        chunks = [args[i:i+2] for i in range(0, len(args), 2)]
    elif arity == 3:
        chunks = [args[i:i+3] for i in range(0, len(args), 3)]
    else:
        chunks = [args[i:i+1] for i in range(0, len(args), 1)]
        
    current_line_chunks = []
    current_len = len(name)
    
    for chunk in chunks:
        chunk_str = " " + " ".join(chunk)
        if current_len + len(chunk_str) > 70:
            safe_lines.append(name + "".join(current_line_chunks))
            current_line_chunks = []
            current_len = len(name)
        
        current_line_chunks.append(chunk_str)
        current_len += len(chunk_str)
        
    if current_line_chunks:
        safe_lines.append(name + "".join(current_line_chunks))

print(f"Writing safe circuit to circuit_safe.stim ({len(safe_lines)} lines)...")
with open("circuit_safe.stim", "w") as f:
    f.write("\n".join(safe_lines))

print("Done.")
