def check_lengths():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_133.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    for i, line in enumerate(lines):
        if len(line) != 133:
            print(f"Line {i+1} has length {len(line)}")

if __name__ == "__main__":
    check_lengths()
