import stim

try:
    with open("candidate.stim", "r") as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove line numbers if present (e.g. 1. RX ...)
        if '. ' in line[:4]:
            parts = line.split('. ', 1)
            if len(parts) > 1:
                line = parts[1]
        
        if line.startswith("RX"):
            # Replace RX with H for initialization
            parts = line.split()
            # RX ... -> H ...
            new_lines.append("H " + " ".join(parts[1:]))
        elif line.startswith("TICK"):
            continue
        else:
            new_lines.append(line)

    cleaned_content = "\n".join(new_lines)
    
    # Verify it parses
    circuit = stim.Circuit(cleaned_content)
    
    with open("candidate_clean.stim", "w") as f:
        f.write(str(circuit))

    print("Cleaned candidate saved to candidate_clean.stim")

except Exception as e:
    print(f"Error cleaning candidate: {e}")
