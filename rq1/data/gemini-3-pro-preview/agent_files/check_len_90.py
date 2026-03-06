filename = "data/gemini-3-pro-preview/agent_files/stabilizers_90.txt"
with open(filename, "r") as f:
    lines = [line.strip().replace(',', '') for line in f if line.strip()]

print(f"Number of lines: {len(lines)}")
for i, line in enumerate(lines):
    if len(line) != 90:
        print(f"Line {i+1} has length {len(line)}")
