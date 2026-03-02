with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt', 'r') as f:
    lines = f.readlines()
    print(f"Number of lines: {len(lines)}")
    if lines:
        print(f"Length of first line: {len(lines[0].strip())}")
        print(f"First line: {lines[0].strip()}")
