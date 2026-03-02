import stim

def verify_patterns():
    # Pattern 1: XIIIXIIIIIIIXIX
    # X at 0, 4, 12, 16, 18?
    # Let's check line 27.
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    s27 = lines[27]
    # Find first X
    first_X = s27.find('X')
    print(f"Line 27 first X at: {first_X}")
    # Extract pattern
    # It seems to be XIIIXIIIIIIIXIX
    # Indices relative to first X:
    # 0: X
    # 1-3: III
    # 4: X
    # 5-11: IIIIIII (7 Is)
    # 12: X
    # 13: I
    # 14: X
    
    # Wait, check 34 vs 79
    # 34 starts at 121.
    # Pattern at 121.
    # X at 121+0 = 121.
    # X at 121+4 = 125.
    # X at 121+12 = 133.
    # X at 121+14 = 135.
    
    # Line 79
    # Block starting at 72.
    # Pattern ZIIIZIZZ
    # Let's check line 72.
    s72 = lines[72]
    first_Z = s72.find('Z')
    print(f"Line 72 first Z at: {first_Z}")
    
    # Line 79 is index 7 in block (72+7=79).
    # Start = first_Z + 7*17.
    
    # Let's see where they overlap.
    pass

if __name__ == "__main__":
    verify_patterns()
