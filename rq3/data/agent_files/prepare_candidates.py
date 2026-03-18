import stim

def main():
    # Read candidate 1 (CX based, shorter)
    with open("candidate_graph.stim", "r") as f:
        c1 = f.read()
    
    # Read candidate 2 (CZ based) - using the cleaned version
    # Actually, I should clean it properly in python here.
    with open("candidate_elim.stim", "r") as f:
        c2_raw = f.read()
    
    # Clean c2: Replace RX with H, remove TICK
    c2_lines = []
    for line in c2_raw.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("TICK"): continue
        if line.startswith("RX"):
            targets = line.split()[1:]
            c2_lines.append("H " + " ".join(targets))
        else:
            c2_lines.append(line)
    c2 = "\n".join(c2_lines)

    print("Evaluating Candidate 1 (CX based)...")
    # I cannot call the tool from python directly, I must use the tool call.
    # So I will just prepare the files and then call the tool.
    
    with open("candidate1.stim", "w") as f:
        f.write(c1)
        
    with open("candidate2.stim", "w") as f:
        f.write(c2)

if __name__ == "__main__":
    main()
