import stim

def format_circuit():
    with open('candidate.stim', 'r') as f:
        c = stim.Circuit(f.read())
    
    # We want to print it such that lines are short
    for instr in c:
        name = instr.name
        targets = instr.targets_copy()
        args = instr.gate_args_copy()
        
        line = name
        if args:
            line += "(" + ",".join(str(a) for a in args) + ")"
        
        print(line, end="")
        current_len = len(line)
        for t in targets:
            # Handle different target types if needed, but here mostly qubit indices
            s = str(t.value)
            if current_len + len(s) + 1 > 70:
                print("\n  ", end="")
                current_len = 2
            print(" " + s, end="")
            current_len += len(s) + 1
        print("")

if __name__ == "__main__":
    format_circuit()
