def fix_file():
    with open('stabilizers_148.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Fix line 127 (index 127)
    # It has length 146. Needs 2 more chars.
    # It should match the shift pattern.
    # The Z is at 111, should be at 113.
    # So we need to insert 2 Is at the beginning.
    lines[127] = "II" + lines[127]
    
    # Fix line 134 (index 134)
    # It has length 150. Needs 2 fewer chars.
    # Z is at 81. Should be at 79?
    # Let's check the pattern.
    # 133: Z at 44.
    # 134: Z at 81. 44 + 37 = 81.
    # 135: Z at 118. 81 + 37 = 118.
    # So the Z position is correct relative to neighbors!
    # But length is 150.
    # Maybe extra Is at the end?
    # Or extra Is at the beginning?
    # If Z is at 81, and length is 150.
    # If we remove 2 Is from the end, length becomes 148. Z remains at 81.
    # If we remove 2 Is from the beginning, Z becomes 79.
    
    # Let's check 133 again. Z at 44.
    # 134 should have Z at 44 + 37 = 81.
    # So the Z position 81 is correct!
    # So the extra characters must be at the end (or not affecting the Z position).
    # Removing from the end seems safest if it's all Is.
    if len(lines[134]) > 148:
        print(f"Truncating line 134 from {len(lines[134])} to 148")
        lines[134] = lines[134][:148]
    
    with open('stabilizers_148.txt', 'w') as f:
        for line in lines:
            f.write(line + '\n')

    print("Fixed lengths.")

fix_file()
