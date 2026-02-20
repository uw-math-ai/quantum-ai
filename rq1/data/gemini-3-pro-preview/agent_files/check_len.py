with open('data/gemini-3-pro-preview/agent_files/stabilizers.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

for i, line in enumerate(lines):
    if len(line) != 102:
        print(f"Line {i}: Length {len(line)}")
        print(line)
