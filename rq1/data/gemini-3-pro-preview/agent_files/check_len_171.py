with open("data/gemini-3-pro-preview/agent_files/stabilizers_171.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Number of lines: {len(lines)}")
print(f"Length of first line: {len(lines[0])}")
print(f"Length of last line: {len(lines[-1])}")

for i, line in enumerate(lines):
    if len(line) != 171:
        print(f"Line {i} has length {len(line)}")
