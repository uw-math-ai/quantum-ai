with open('target_stabilizers_196.txt', 'r') as f:
    for i, line in enumerate(f):
        line = line.strip()
        if len(line) != 196:
            print(f"Line {i+1}: length {len(line)}")
            print(f"Content: {line}")
