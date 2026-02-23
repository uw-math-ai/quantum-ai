import stim

def fix_stabilizers():
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    new_lines = list(lines)
    
    # --- Fix Line 43 ---
    # Pattern: XXXXXIXXIIIIX (length 13)
    # Block shift 17.
    # Line 42 starts at 106.
    # Line 43 should start at 123.
    pattern_43 = "XXXXXIXXIIIIX"
    s43 = "I"*123 + pattern_43 + "I"*(153 - 123 - len(pattern_43))
    new_lines[43] = s43
    print(f"Fixed 43: {s43}")

    # --- Fix Line 51 ---
    # Block starts at 45.
    # Line 45: IXIIXIIIIIXIIXIIII...
    # Wait, line 45 is IXIIXIIIIIXIIX...
    # Let's check pattern length.
    # IXIIXIIIIIXIIX (length 14)
    # Shift 17.
    # Line 51 is index 6 in block (45+6=51).
    # Start: 0 + 6*17 = 102.
    # Wait, line 45 starts at 0.
    # Line 51 starts at 102.
    # Let's check line 51 content in file.
    # It has "XIIXIIIIIXIIX" inside.
    # But line 45 starts with "IXII...".
    # Is the pattern "IXII..." or just "XII..."?
    # Let's check line 46.
    # Line 46: IIIIIIIIIIIIIIIIIIXIIXIIIIIXIIX...
    # It starts at 18?
    # 18 - 0 = 18?
    # Let's check line 47.
    # Starts at 35? 35 - 18 = 17.
    # Maybe line 45 is special?
    # Or maybe the pattern is length 14 starting at 0.
    # Line 46 starts at 17?
    # "II...II" (17 Is) + "IXII..."?
    # Let's look at line 46 in the bad file.
    # I'll just print it.
    
    # --- Fix Line 109 ---
    # Block starts at 108.
    # Line 108: IIIIZZZZZIZZIIIIZIIII...
    # Pattern: ZZZZZIZZIIIIZ (length 13)
    # Line 108 starts at 4?
    # Line 109 starts at 21?
    # Shift 17?
    # 21 - 4 = 17.
    # Line 109 has length 151.
    # 109 is index 1 in block (108+1=109).
    # Start: 4 + 17 = 21.
    # Reconstruct: 21 Is + Pattern + Rest.
    pattern_109 = "ZZZZZIZZIIIIZ"
    s109 = "I"*21 + pattern_109 + "I"*(153 - 21 - len(pattern_109))
    new_lines[109] = s109
    print(f"Fixed 109: {s109}")
    
    # Write corrected file
    out_path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt'
    with open(out_path, 'w') as f:
        for line in new_lines:
            f.write(line + '\n')
            
    return new_lines

def analyze_block_51_pattern(lines):
    # Print lines 45, 46, 47 to deduc shift
    print(f"45: {lines[45]}")
    print(f"46: {lines[46]}")
    print(f"47: {lines[47]}")
    # Print 51 original
    print(f"51: {lines[51]}")

if __name__ == "__main__":
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    analyze_block_51_pattern(lines)
    
    # I'll manually fix 51 in the next step after seeing the pattern.
    # But for 43 and 109 I am reasonably confident.
    pass
