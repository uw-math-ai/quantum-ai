with open("target_stabilizers.txt", "r") as f:
    line = f.readline().strip()
    print(f"Length of stabilizer string: {len(line)}")
