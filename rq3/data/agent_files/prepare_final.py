import stim

try:
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate.stim", "r") as f:
        content = f.read()
    
    # Replace RX with H
    # RX appears as "RX 0 1 2 ..."
    # We can just replace "RX" with "H" if it's the instruction name
    # But be careful not to replace partial strings.
    # Stim format: instruction name, then targets.
    # Since RX is at the start, it's likely fine.
    # But better to parse and replace.
    
    c = stim.Circuit(content)
    new_c = stim.Circuit()
    for instr in c:
        if instr.name == "RX":
            # Replace with H
            new_c.append("H", instr.targets_copy())
        else:
            new_c.append(instr)
            
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\candidate_final.stim", "w") as f:
        f.write(str(new_c))
        
    print("Replaced RX with H.")
    
except Exception as e:
    print(e)
