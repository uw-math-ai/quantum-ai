def check_lines():
    with open('stabilizers_148.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Line 127 (0-indexed) is the 128th line
    # Line 134 (0-indexed) is the 135th line
    
    # Python 0-indexed:
    l127 = lines[127]
    l134 = lines[134]
    
    print(f"Line 127 len: {len(l127)}")
    print(f"Line 134 len: {len(l134)}")
    
    # Compare with neighbors
    l126 = lines[126]
    l128 = lines[128]
    
    print(f"\nAnalysis of group 125-128:")
    for i in range(125, 129):
        s = lines[i]
        first_z = s.find('Z')
        print(f"{i}: len={len(s)}, first_Z at {first_z}")
        
    print(f"\nAnalysis of group 133-136:")
    for i in range(133, 137):
        s = lines[i]
        # Find first non-I
        first_nz = -1
        for k, c in enumerate(s):
            if c != 'I':
                first_nz = k
                break
        print(f"{i}: len={len(s)}, first_non_I at {first_nz}, char={s[first_nz]}")

check_lines()
