with open("stabilizers_186.txt", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    clean = line.strip()
    if len(clean) != 186:
        print(f"Line {i}: length {len(clean)}")
        if len(clean) < 50:
             print(f"  Content: {clean}")
