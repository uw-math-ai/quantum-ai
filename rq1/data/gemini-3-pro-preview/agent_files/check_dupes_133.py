def check_dupes():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_133.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    seen = {}
    for i, line in enumerate(lines):
        if line in seen:
            print(f"Duplicate found: Line {i} matches Line {seen[line]}")
        seen[line] = i
        
    print(f"Total lines: {len(lines)}")
    print(f"Unique lines: {len(seen)}")

if __name__ == "__main__":
    check_dupes()
