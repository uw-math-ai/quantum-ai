import sys

def solve():
    path = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_150.txt'
    with open(path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Correct the lengths by truncating to 150 if they are longer
    # But wait, maybe they are just wrong?
    # Let's inspect line 20
    line20 = lines[20]
    print(f"Line 20: {line20}")
    print(f"Len: {len(line20)}")
    
    # If it is 152, maybe it has spaces inside?
    if ' ' in line20:
        print("Line 20 has spaces")
        
    # Let's try to fix all lines to be 150
    fixed_lines = []
    for line in lines:
        if len(line) > 150:
             # Assume extra chars are at end or start? Or duplicate?
             # Let's check if it matches the pattern
             # The pattern is XXIIIXX shifted.
             # If I remove 2 chars, where?
             # Let's just truncate for now and see if it makes sense.
             fixed_lines.append(line[:150])
        elif len(line) < 150:
             print(f"Line too short: {len(line)}")
             fixed_lines.append(line) # Can't easily fix
        else:
             fixed_lines.append(line)

    with open(path, 'w') as f:
        for line in fixed_lines:
            f.write(line + '\n')
            
if __name__ == "__main__":
    solve()
