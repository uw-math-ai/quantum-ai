with open('target_stabilizers_job.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

fixed_lines = []
for line in lines:
    if len(line) == 169:
        line = line + "II"
    fixed_lines.append(line)

with open('target_stabilizers_fixed.txt', 'w') as f:
    for line in fixed_lines:
        f.write(line + "\n")

print(f"Fixed {len(lines)} lines.")
