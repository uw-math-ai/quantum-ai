import stim

def clean():
    with open("candidate_raw_v2.stim", "r") as f:
        text = f.read()
    
    # Remove TICK
    text = text.replace("TICK\n", "")
    text = text.replace("TICK", "")
    
    # Process RX
    # Stim's graph state output uses RX for initialization.
    # We replace RX with H.
    # But RX takes a list of targets.
    # "RX 0 1 2" -> "H 0 1 2"
    # This works because RX resets to |+> and H on |0> prepares |+>.
    # Assuming start state is |0>.
    
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith("RX"):
            # Replace RX with H
            new_lines.append(line.replace("RX", "H"))
        else:
            new_lines.append(line)
            
    final_text = "\n".join(new_lines)
    
    # Write to candidate_cleaned.stim
    with open("candidate_cleaned.stim", "w") as f:
        f.write(final_text)

    print("Cleaned circuit written to candidate_cleaned.stim")

if __name__ == "__main__":
    clean()
