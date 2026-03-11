with open('target_stabilizers_job.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

indices = [81, 145, 147]
for i in indices:
    print(f"\nLine {i}:")
    print(lines[i])
    print(f"Len: {len(lines[i])}")
    if i > 0:
        print(f"Prev Line {i-1}:")
        print(lines[i-1])
        print(f"Len: {len(lines[i-1])}")
    if i < len(lines) - 1:
        print(f"Next Line {i+1}:")
        print(lines[i+1])
        print(f"Len: {len(lines[i+1])}")
