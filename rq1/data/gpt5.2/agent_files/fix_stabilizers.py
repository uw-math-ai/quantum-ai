import re

def analyze_and_fix():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\solve_85_v2.py', 'r') as f:
        lines = f.readlines()
        
    stabilizers = []
    start_line = -1
    for i, line in enumerate(lines):
        if "stabilizers = [" in line:
            start_line = i + 1
            break
            
    if start_line == -1:
        print("Could not find stabilizers start")
        return

    fixed_lines = lines[:]
    
    # Process stabilizers until "]"
    for i in range(start_line, len(lines)):
        line = lines[i].strip()
        if line == "]":
            break
        
        if not line.startswith('"'):
            continue
            
        # Extract the string
        s = line.strip('",')
        original_len = len(s)
        
        if original_len == 85:
            continue
            
        print(f"Line {i} (Stab {i-start_line}): Length {original_len}")
        
        # Determine the pattern (XZZX, XIXZZ, ZXIXZ, XXXXX...?)
        # For the first part, it is XZZX.
        # Check if we can just trim Is from the beginning or end.
        # But we need to know the correct position.
        
        # Let's try to infer from neighbors.
        # But simply: if length is 87, and it looks like it has too many Is.
        # Let's look at the structure.
        # If it has leading Is and trailing Is.
        
        # Let's just try to fix it by removing 2 Is from the beginning if it helps align?
        # Or maybe it's better to just fix it based on the expected shift.
        
        # Let's count leading Is.
        leading_is = len(s) - len(s.lstrip('I'))
        
        # Expected leading Is?
        # It seems the blocks are size 17 (0-16, 17-33, 34-50, 51-67).
        # Shift is 5.
        # Block 0 starts at 0.
        # Block 1 starts at 1.
        # Block 2 starts at 2?
        # Let's check block starts.
        # 0: 0
        # 17: 1 (IXZZX...)
        # 34: 0 (XIXZZ...)
        # 51: 0 (ZXIXZ...)
        
        # Wait, let's look at 34 (Stab 34).
        # "XIXZZ..." -> Index 0.
        # 51 (Stab 51).
        # "ZXIXZ..." -> Index 0.
        
        # So maybe blocks 0, 2, 3 start at 0?
        # Block 1 starts at 1?
        
        # Let's check Stab 31 again.
        # It is in block 0 (0-33).
        # Wait, if block size is 17, then 0-16 is block 0.
        # 17-33 is block 1.
        # So Stab 31 is in block 1.
        # Block 1 starts at index 1.
        # Stab 17 has 1 I.
        # Stab 18 has 6 Is.
        # ...
        # Stab k (in block 1) should have 1 + (k-17)*5 Is.
        # Stab 31: k=31. 31-17 = 14.
        # 1 + 14*5 = 71 Is.
        
        # Let's check what Stab 31 has.
        # It had length 87.
        # Pattern is XZZX (length 4).
        # 87 - 4 = 83 Is.
        # Trailing Is?
        # 85 - 71 - 4 = 10.
        # So correct should be: 71 Is + XZZX + 10 Is.
        
        # If current has 83 Is.
        # If it has 73 Is at start?
        # 73 + 4 + 10 = 87.
        # So remove 2 Is from start.
        
        # Let's verify Stab 14 (in block 0).
        # Block 0 starts at 0.
        # k=14. 14*5 = 70.
        # 70 Is + XZZX + 11 Is = 85.
        # It had 87 length. I fixed it to have 70 Is.
        
        # Stab 48 (in block 2).
        # Block 2 starts at 34.
        # k=48. 48-34 = 14.
        # 14*5 = 70.
        # 70 Is + XIXZZ (5 chars) + 10 Is = 85.
        # It had 87 length. I fixed it to have 70 Is.
        
        # So the logic holds.
        
        # Let's apply this logic.
        idx = i - start_line
        
        # Determine block
        if 0 <= idx <= 16:
            start_offset = 0
            block_start_idx = 0
            pattern_len = 4 # XZZX
        elif 17 <= idx <= 33:
            start_offset = 1
            block_start_idx = 17
            pattern_len = 4 # XZZX
        elif 34 <= idx <= 50:
            start_offset = 0
            block_start_idx = 34
            pattern_len = 5 # XIXZZ
        elif 51 <= idx <= 67:
            start_offset = 0
            block_start_idx = 51
            pattern_len = 5 # ZXIXZ
        else:
            # Other blocks
            continue
            
        expected_leading_is = start_offset + (idx - block_start_idx) * 5
        
        # Check if we have enough characters
        # Find the pattern
        # Just strip Is and see what remains
        content = s.replace('I', '')
        # Verify content matches pattern roughly (or just preserve it)
        
        # Reconstruct
        new_s = 'I' * expected_leading_is + content + 'I' * (85 - expected_leading_is - len(content))
        
        if len(new_s) != 85:
            print(f"  Warning: Could not fix line {i} to length 85. Result len {len(new_s)}")
        else:
            print(f"  Fixing line {i}: {len(s)} -> {len(new_s)}")
            lines[i] = '        "' + new_s + '",\n'

    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\solve_85_v2.py', 'w') as f:
        f.writelines(lines)

if __name__ == "__main__":
    analyze_and_fix()
