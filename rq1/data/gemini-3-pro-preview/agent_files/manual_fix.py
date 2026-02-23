def manual_fix(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    fixed_lines = lines[:]
    
    # Line 24: Prepend I
    if len(lines[23]) == 74:
        fixed_lines[23] = 'I' + lines[23]
        print(f"Fixed line 24: {fixed_lines[23]}")
    else:
        print(f"Line 24 length {len(lines[23])}, skipping fix.")

    # Line 25: Trim 2 chars from end? Or beginning?
    # Expected shift: 1 + 9*5 = 46.
    # Current: 46 I's.
    # Length 77. 46 + 4 + 27 = 77.
    # Expected length 75.
    # If we trim 2 from end, we get 46 + 4 + 25 = 75.
    if len(lines[24]) == 77:
        fixed_lines[24] = lines[24][:75]
        print(f"Fixed line 25: {fixed_lines[24]}")

    # Line 40: Length 77.
    # Group 3 (XIXZZ). Starts at 31.
    # 31: Shift 0? `XIXZZ...`
    # 32: Shift 5? `IIIIIXIXZZ...`
    # ...
    # 40: Shift (40-31)*5 = 45.
    # Line 40 content: `IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIIIII`
    # 45 I's.
    # 45 + 5 (XIXZZ) + 27 I's = 77.
    # Expected 75. Trim 2 from end.
    if len(lines[39]) == 77:
        fixed_lines[39] = lines[39][:75]
        print(f"Fixed line 40: {fixed_lines[39]}")

    # Line 55: Length 77.
    # Group 4 (ZXIXZ). Starts at 46.
    # 46: Shift 0.
    # ...
    # 55: Shift (55-46)*5 = 45.
    # Line 55 content: `IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIII`
    # 45 I's + 5 + 27 I's = 77.
    # Expected 75. Trim 2 from end.
    if len(lines[54]) == 77:
        fixed_lines[54] = lines[54][:75]
        print(f"Fixed line 55: {fixed_lines[54]}")

    with open(filename, 'w') as f:
        for line in fixed_lines:
            f.write(line + '\n')

if __name__ == "__main__":
    manual_fix(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt')
