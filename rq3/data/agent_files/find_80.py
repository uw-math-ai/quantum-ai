with open("current_baseline.stim", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "80" in line:
        print(f"Line {i+1}: {line.strip()}")
