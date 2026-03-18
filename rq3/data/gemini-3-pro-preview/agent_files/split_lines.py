
import stim

c = stim.Circuit.from_file('candidate_graph_final.stim')
new_c = stim.Circuit()

for instruction in c:
    name = instruction.name
    targets = instruction.targets_copy()
    args = instruction.gate_args_copy()
    
    # Split into chunks of, say, 10 targets
    chunk_size = 8
    
    if name in ["CX", "CZ", "SWAP", "ISWAP"]:
        # These take pairs. So chunk size must be even.
        chunk_size = 8 # 4 pairs
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            new_c.append(name, chunk, args)
    else:
        # Single qubit gates
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            new_c.append(name, chunk, args)

with open('candidate_split.stim', 'w') as f:
    f.write(str(new_c))
