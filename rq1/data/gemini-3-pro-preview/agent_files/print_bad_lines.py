def print_lines(lines):
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    with open(path, 'r') as f:
        all_lines = [line.strip() for line in f if line.strip()]
    
    for k in lines:
        if k < len(all_lines):
            print(f"{k} (len {len(all_lines[k])}): {all_lines[k]}")

if __name__ == "__main__":
    print_lines([42, 43, 44, 50, 51, 52, 108, 109, 110])
