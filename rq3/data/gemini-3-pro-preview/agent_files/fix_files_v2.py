with open("target_stabilizers_rq3_new_v5.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

fixed_lines = []
for l in lines:
    if len(l) > 120:
        print(f"Truncating line from {len(l)} to 120: {l[:120]}...")
        fixed_lines.append(l[:120])
    else:
        fixed_lines.append(l)

with open("target_stabilizers_rq3_new_v5.txt", "w") as f:
    for l in fixed_lines:
        f.write(l + "\n")
