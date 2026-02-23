def check_block_counts():
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    print(f"Total lines: {len(lines)}")
    
    # Blocks start at 0, 9, 18...
    # Let's assume the first line of each block starts with a pattern or something.
    # Block 1 starts with 'IIIIIXIIIXIXX...'
    # Block 2 starts with 'IIIIIIIIXIXIIXIX...' (index 9)
    # Block 3 starts with 'IIIXIIIXIIIIIIXIX...' (index 18)
    
    # Let's print line 8, 9, 17, 18, 26, 27...
    
    indices = [8, 9, 17, 18, 26, 27, 35, 36, 44, 45, 53, 54, 62, 63, 71, 72, 80, 81, 89, 90, 98, 99, 107, 108, 116, 117, 125, 126, 134, 135, 143, 144]
    
    for i in indices:
        if i < len(lines):
            print(f"Line {i}: {lines[i][:20]}...")
        else:
            print(f"Line {i}: MISSING")

if __name__ == "__main__":
    check_block_counts()
