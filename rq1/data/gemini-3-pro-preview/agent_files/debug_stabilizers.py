with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_100.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

for i, line in enumerate(lines):
    if len(line) != 100:
        print(f"Line {i+1}: Length {len(line)}")
        print(f"Content: {line}")
        # Print where the extra chars might be?
