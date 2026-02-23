with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_42.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

for i, line in enumerate(lines):
    if len(line) != 42:
        print(f"Line {i+1} has length {len(line)}: {line}")
