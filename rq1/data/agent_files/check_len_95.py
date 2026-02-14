with open("stabilizers_95.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

for i, line in enumerate(lines):
    if len(line) != 95:
        print(f"Line {i} length {len(line)}: {line}")
