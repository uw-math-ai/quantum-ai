import stim

c = stim.Circuit.from_file("best_candidate.stim")
text = str(c).replace("TICK", "")

# Reformat to avoid long lines
lines = []
current_line = []
for token in text.split():
    if token in ["RX", "CZ", "H", "S", "X", "Y", "Z", "TICK", "R", "M", "CX"]:
        if current_line:
            lines.append(" ".join(current_line))
        current_line = [token]
    else:
        current_line.append(token)
        if len(current_line) > 20: # limit line length
             lines.append(" ".join(current_line))
             current_line = []

if current_line:
    lines.append(" ".join(current_line))

final_text = "\n".join(lines)
print(final_text)
