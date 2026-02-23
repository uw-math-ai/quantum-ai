import stim

def reformat_manual():
    with open("circuit_135_solution.stim", "r") as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    
    # Manually print instructions
    output = []
    for instruction in circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        
        # Split into small chunks
        chunk_size = 2 # pairs for 2-qubit gates, or just small number
        if name in ["CX", "CZ", "SWAP", "M", "R", "X", "Y", "Z", "H"]:
             step = 2 if name in ["CX", "CZ", "SWAP"] else 1
             for i in range(0, len(targets), step):
                 group = targets[i:i+step]
                 # Convert targets to string (handle lookback etc if needed, but here we expect integers)
                 t_str = " ".join(str(t.value) for t in group)
                 output.append(f"{name} {t_str}")
        else:
            output.append(str(instruction))
            
    # Join with newlines
    final_str = "\n".join(output)
    print(final_str)

if __name__ == "__main__":
    reformat_manual()
