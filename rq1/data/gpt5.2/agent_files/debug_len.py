lines = open("stabilizers_135.txt").read().splitlines()
lines = [l.strip() for l in lines if l.strip()]

for i, line in enumerate(lines):
    if len(line) != 135:
        print(f"Line {i}: len={len(line)} content={line}")
