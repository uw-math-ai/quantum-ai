import stim

with open('candidate_clean.stim', 'r') as f:
    circuit = stim.Circuit(f.read())

# Reformat: one gate per line, max 10 targets per line?
# Or just iterate instructions and print them.
# Stim's string representation is usually compact.
# But for safety, let's break down the CZ block.

formatted_lines = []
for op in circuit:
    if op.name == "CZ":
        # Split into multiple CZ lines if too long?
        # Actually, let's just print it. If it's one huge line, I'll just have to trust the tool handles long strings.
        # But to be safe against copy-paste wrapping, I'll split it.
        targets = op.targets_copy()
        # Group by 2 (since CZ is 2-qubit)
        pairs = [targets[i:i+2] for i in range(0, len(targets), 2)]
        
        # Output 10 pairs per line
        chunk_size = 10
        for i in range(0, len(pairs), chunk_size):
            chunk = pairs[i:i+chunk_size]
            t_str = " ".join(f"{p[0].value} {p[1].value}" for p in chunk)
            formatted_lines.append(f"CZ {t_str}")
    else:
        # For single qubit gates, also split if too long
        targets = op.targets_copy()
        t_vals = [t.value for t in targets]
        if len(t_vals) > 20:
             for i in range(0, len(t_vals), 20):
                 chunk = t_vals[i:i+20]
                 t_str = " ".join(str(v) for v in chunk)
                 formatted_lines.append(f"{op.name} {t_str}")
        else:
             formatted_lines.append(str(op))

final_text = "\n".join(formatted_lines)
with open('candidate_formatted.stim', 'w') as f:
    f.write(final_text)

print(final_text)
