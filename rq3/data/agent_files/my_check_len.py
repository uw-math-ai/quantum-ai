with open("current_stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

lengths = [len(l) for l in lines]
print(f"Lengths: {set(lengths)}")
for i, l in enumerate(lines):
    if len(l) != 60:
        print(f"Line {i} has length {len(l)}: '{l}'")
