def print_lines(start, end):
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    for k in range(start, end+1):
        if k < len(lines):
            print(f"{k}: {lines[k]}")

if __name__ == "__main__":
    print("--- Around 34 ---")
    print_lines(30, 40)
    print("--- Around 79 ---")
    print_lines(75, 85)
