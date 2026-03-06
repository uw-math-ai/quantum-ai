def check_lengths():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\my_stabilizers_72.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    for i, line in enumerate(lines):
        if len(line) != 72:
            print(f"Line {i+1} has length {len(line)}: {line}")
            
    print(f"Checked {len(lines)} lines.")

if __name__ == "__main__":
    check_lengths()
