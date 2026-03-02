def solve():
    path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_150.txt'
    with open(path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    for i, line in enumerate(lines):
        if len(line) != 150:
            print(f"Line {i} has length {len(line)}: {line}")
        else:
            pass # correct length

if __name__ == "__main__":
    solve()
