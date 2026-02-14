with open("target_stabilizers.txt", "r") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        print(len(line))
        if len(line) != 72:
            print(f"Line '{line[:10]}...' has length {len(line)}")
        break
