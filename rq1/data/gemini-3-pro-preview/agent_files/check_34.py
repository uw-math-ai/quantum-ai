def check_34_shift():
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    s34 = lines[34]
    first_X = s34.find('X')
    print(f"Line 34 first X at: {first_X}")
    
    # Calculate expected shift
    # Block 27 starts at 2.
    # 34 should be 2 + 7*17 = 121.
    
    # If first_X is 119, then line 34 is shifted incorrectly.
    # 119 vs 121. Difference 2.
    
    # Let's check other lines in block 27.
    for i in range(27, 36):
        line = lines[i]
        fx = line.find('X')
        expected = 2 + (i-27)*17
        print(f"Line {i}: Start {fx}, Expected {expected}, Diff {fx-expected}")

if __name__ == "__main__":
    check_34_shift()
