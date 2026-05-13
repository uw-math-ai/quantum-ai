
with open("solution.stim", "r") as f:
    lines = f.readlines()

new_lines = []
current_line = ""

for line in lines:
    line = line.strip()
    if not line: continue
    
    # Check if line starts with a gate name
    # Valid gates: CX, H, M, S, S_DAG, R, RX, RY, RZ, DETECTOR, OBSERVABLE_INCLUDE
    # Or just check if it starts with a letter?
    if line[0].isalpha():
        if current_line:
            new_lines.append(current_line)
        current_line = line
    else:
        # Continuation
        current_line += " " + line

if current_line:
    new_lines.append(current_line)

with open("solution_fixed.stim", "w") as f:
    for l in new_lines:
        f.write(l + "\n")
