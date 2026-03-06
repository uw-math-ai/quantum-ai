import stim

def clean_candidate():
    with open("candidate_prompt.stim", "r") as f:
        content = f.read()
        
    # Replace RX with H
    # RX resets to |+>. H on |0> (initial) is |+>.
    # So valid replacement.
    content = content.replace("RX", "H")
    
    # Remove TICKs
    lines = [l for l in content.splitlines() if not l.strip().startswith("TICK")]
    
    new_content = "\n".join(lines)
    
    with open("candidate_submission.stim", "w") as f:
        f.write(new_content)
        
    print("Cleaned candidate saved to candidate_submission.stim")

if __name__ == "__main__":
    clean_candidate()
