import stim

circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_68.stim")

new_circuit = stim.Circuit()
for instruction in circuit:
    if len(instruction.targets_copy()) > 10:
        # Split large instructions
        name = instruction.name
        targets = instruction.targets_copy()
        args = instruction.gate_args_copy()
        
        # Process targets in chunks
        # Note: some gates like CX consume 2 targets at a time.
        # H consumes 1.
        arity = 1
        if name in ["CX", "CNOT", "CZ", "SWAP", "ISWAP", "XCX", "XCY", "XCZ", "YCX", "YCY", "YCZ", "ZCX", "ZCY", "ZCZ"]:
            arity = 2
        
        chunk_size = 10
        # Make sure chunk_size is divisible by arity
        if chunk_size % arity != 0:
            chunk_size -= (chunk_size % arity)
            
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            new_circuit.append(name, chunk, args)
    else:
        new_circuit.append(instruction)

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_68_short_lines.stim", "w") as f:
    f.write(str(new_circuit))
