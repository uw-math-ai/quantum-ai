lines = [l.strip() for l in open('stabilizers_171.txt') if l.strip()]

print("Analyzing lines 50-70:")
for i in range(50, 71):
    if i < len(lines):
        line = lines[i]
        idx = line.find('X')
        print(f"{i}: X at {idx}, len {len(line)}")
        if len(line) != 171:
            print(f"    ERROR: {line}")

print("\nAnalyzing lines 130-150:")
for i in range(130, 151):
    if i < len(lines):
        line = lines[i]
        idx = line.find('Z') if 'Z' in line else line.find('X')
        print(f"{i}: X/Z at {idx}, len {len(line)}")
        if len(line) != 171:
            print(f"    ERROR: {line}")
