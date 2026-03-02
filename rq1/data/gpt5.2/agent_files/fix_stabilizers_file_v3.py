def fix_stabilizers():
    with open('stabilizers_119.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    fixed_lines = []
    for i, line in enumerate(lines):
        # Fix length to 119
        if len(line) > 119:
            # If it has leading Is and trailing Is, try to center or trim ends
            # But here most seem to be simple padding issues
            # For line 96 (index 95) which is 121 chars:
            # It's IIII...ZIIZIIIIIZIIZ...IIII
            # We should trim 2 chars. Likely from the end if it's just padding.
            # Or check the pattern alignment.
            fixed_line = line[:119]
        elif len(line) < 119:
            fixed_line = line + 'I' * (119 - len(line))
        else:
            fixed_line = line
        
        fixed_lines.append(fixed_line)

    with open('stabilizers_119_fixed_v2.txt', 'w') as f:
        for line in fixed_lines:
            f.write(line + '\n')

fix_stabilizers()
