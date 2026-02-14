stabs = []
with open('stabilizers_105.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

for i, line in enumerate(lines):
    if len(line) != 105:
        print(f"Line {i+1}: length {len(line)}")
    else:
        stabs.append(line)

print(f"Found {len(stabs)} valid stabilizers of length 105.")
if len(stabs) == len(lines):
    print("All stabilizers are length 105.")
else:
    print(f"Found {len(lines) - len(stabs)} bad lines.")
