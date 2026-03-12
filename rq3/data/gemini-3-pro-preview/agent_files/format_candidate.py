import stim

def format_circuit():
    try:
        with open("candidate_graph.stim", "r") as f:
            content = f.read()
            c = stim.Circuit(content)
    except Exception as e:
        print(f"Error reading circuit: {e}")
        return

    new_c = stim.Circuit()
    for instruction in c:
        name = instruction.name
        if name in ["TICK", "SHIFT_COORDS", "QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE"]:
            new_c.append(instruction)
            continue
            
        targets = instruction.targets_copy()
        
        # determine step size (arity)
        # simplistic check for standard gates
        if name in ["CZ", "CX", "SWAP", "ISWAP", "CV", "CY", "ZC", "XC"]:
            step = 2
        else:
            step = 1
            
        # Put at most 10 args per line
        chunk_size = 10
        # ensure multiple of step
        if chunk_size % step != 0:
            chunk_size -= (chunk_size % step)
            
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i+chunk_size]
            new_c.append(name, chunk)
            
    with open("candidate_formatted.stim", "w") as f:
        f.write(str(new_c))

if __name__ == "__main__":
    format_circuit()
