import stim

def format_circuit():
    with open("candidate_optimized_v9.stim", "r") as f:
        c = stim.Circuit(f.read())
    
    for instruction in c:
        gate = instruction.name
        targets = instruction.targets_copy()
        
        # CZ and CX and others take pairs.
        # Single qubit gates take 1.
        # Check arity?
        # Stim gate objects don't expose arity directly easily in all versions, 
        # but CZ/CX are 2, others 1.
        # However, for the purpose of valid Stim, we can just split the targets list 
        # as long as we respect the gate's arity.
        # CZ takes pairs. H takes singles.
        
        arity = 1
        if gate in ["CX", "CY", "CZ", "SWAP", "ISWAP", "XCZ", "YCZ", "ZCX", "ZCY"]:
            arity = 2
        
        chunk_size = 20 if arity == 1 else 20 # pairs or singles
        # Ensure chunk_size is even for arity 2
        if arity == 2:
            chunk_size = 20 # 10 pairs
            
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            t_str = " ".join(str(t.value) for t in chunk)
            print(f"{gate} {t_str}")

if __name__ == "__main__":
    format_circuit()
