def check():
    with open('clean_stabilizers.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"Number of lines: {len(lines)}")
    lengths = [len(l) for l in lines]
    print(f"Max length: {max(lengths)}")
    print(f"Min length: {min(lengths)}")
    print(f"Unique lengths: {set(lengths)}")
    
    # Check if any line has length 65
    for i, l in enumerate(lines):
        if len(l) > 63:
            print(f"Line {i} has length {len(l)}: {l}")

if __name__ == "__main__":
    check()
