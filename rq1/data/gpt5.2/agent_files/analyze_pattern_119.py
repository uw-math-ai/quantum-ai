def analyze_pattern():
    filename = r'data\gemini-3-pro-preview\agent_files\stabilizers_119.txt'
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Pattern seems to be:
    # 0-6: X-type
    # 7-13: X-type
    # etc.
    
    # Let's find the first non-I character index for each line.
    for i, line in enumerate(lines):
        first_idx = -1
        for idx, char in enumerate(line):
            if char != 'I':
                first_idx = idx
                break
        
        last_idx = -1
        for idx in range(len(line) - 1, -1, -1):
            if line[idx] != 'I':
                last_idx = idx
                break
                
        print(f"Line {i+1:3d} (len {len(line)}): Start {first_idx:3d}, End {last_idx:3d}, Pattern {line[first_idx:last_idx+1]}")

if __name__ == "__main__":
    analyze_pattern()
