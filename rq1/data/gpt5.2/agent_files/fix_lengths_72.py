with open("stabilizers_72.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

fixed_lines = []
for line in lines:
    if len(line) > 72:
        fixed_lines.append(line[:72])
    else:
        fixed_lines.append(line)

with open("stabilizers_72_fixed.txt", "w") as f:
    f.write("\n".join(fixed_lines))

print("Fixed stabilizers saved to stabilizers_72_fixed.txt")
