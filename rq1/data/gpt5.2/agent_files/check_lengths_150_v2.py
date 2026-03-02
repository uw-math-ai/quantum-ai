with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_150_v2.txt", "r") as f:
    for i, line in enumerate(f):
        line = line.strip()
        if len(line) != 150:
            print(f"Line {i}: {len(line)}")
