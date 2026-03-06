import stim

def safe_print(circuit):
    for instr in circuit:
        if instr.name in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS"]:
            continue
        
        targets = instr.targets_copy()
        if not targets:
            continue
            
        name = instr.name
        arity = 1
        if name in ["CX", "CNOT", "CY", "CZ", "SWAP"]:
            arity = 2
        
        # Split into chunks
        chunk_size = 10 * arity # 10 gates per line
        
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            # Convert targets to string (handling special targets if any, but here just integers)
            # stim targets can be integers or rec(-k) or sweep[k].
            # Here we expect integers.
            s_chunk = " ".join(str(t.value) for t in chunk)
            print(f"{name} {s_chunk}")

c = stim.Circuit.from_file("best_candidate.stim")
safe_print(c)
