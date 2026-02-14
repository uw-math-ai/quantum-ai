def check_lengths(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    lengths = {}
    for i, line in enumerate(lines):
        l = len(line)
        if l not in lengths:
            lengths[l] = []
        lengths[l].append(i)
    
    print("Lengths distribution:")
    for l, indices in lengths.items():
        print(f"Length {l}: {len(indices)} lines (e.g. {indices[:3]})")

check_lengths('stabilizers_75.txt')
