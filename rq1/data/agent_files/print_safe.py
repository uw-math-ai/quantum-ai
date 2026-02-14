with open("circuit_161.stim", "r") as f:
    circuit = f.read()
    # Print with explicit newlines only where the file has them.
    # But to avoid console wrapping issues, I will replace spaces with newlines? No, that makes it too long.
    # I will break lines every 80 chars but ONLY at spaces.
    
    import textwrap
    # Actually, stim format allows newlines anywhere between tokens.
    # So I can just reformat it to have short lines.
    
    import stim
    c = stim.Circuit(circuit)
    print(str(c))
