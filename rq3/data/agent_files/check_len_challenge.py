def check():
    with open('target_stabilizers_challenge.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    print(f"Number of stabilizers: {len(lines)}")
    if lines:
        print(f"Length of first stabilizer: {len(lines[0])}")
        print(f"First stabilizer: {lines[0]}")
        
        # Check all lengths
        lengths = [len(l) for l in lines]
        print(f"Max length: {max(lengths)}")
        print(f"Min length: {min(lengths)}")
        
        for i, l in enumerate(lines):
            if len(l) > 92:
                print(f"Line {i} has length {len(l)}: {l}")
                print(f"Suffix: {l[92:]}")

if __name__ == "__main__":
    check()
