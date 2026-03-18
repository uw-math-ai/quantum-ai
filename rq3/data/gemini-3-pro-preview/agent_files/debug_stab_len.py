with open("target_stabilizers.txt", "r") as f:
    lines = f.readlines()
    print(f"Number of lines: {len(lines)}")
    if lines:
        line0 = lines[0]
        print(f"Line 0 repr: {repr(line0)}")
        print(f"Line 0 len: {len(line0)}")
        print(f"Line 0 stripped len: {len(line0.strip())}")
