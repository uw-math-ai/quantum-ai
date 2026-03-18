with open("target_stabilizers_rq3.txt") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Number of stabilizers: {len(lines)}")
print(f"Length of first stabilizer: {len(lines[0])}")
print(f"Length of last stabilizer: {len(lines[-1])}")
