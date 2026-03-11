import stim

def split_long_lines():
    with open("candidate.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    # Iterate instructions and split if too long
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "CZ" or instr.name == "CX" or instr.name == "H":
            # Split into chunks of pairs (for 2-qubit gates) or singles
            targets = instr.targets_copy()
            chunk_size = 0
            if instr.name in ["CZ", "CX", "SWAP"]:
                chunk_size = 20 # 10 pairs
                step = 2
            else:
                chunk_size = 20
                step = 1
            
            # Process in chunks
            # But wait, targets list is flat.
            # CZ 0 1 2 3 -> pairs (0,1), (2,3)
            # So we take slice [i:i+chunk_size] where chunk_size is even
            
            for i in range(0, len(targets), chunk_size):
                 chunk = targets[i:i+chunk_size]
                 new_circuit.append(instr.name, chunk)
        else:
            new_circuit.append(instr)
            
    with open("candidate_split.stim", "w") as f:
        f.write(str(new_circuit))
    print("Wrote split circuit to candidate_split.stim")

if __name__ == "__main__":
    split_long_lines()
