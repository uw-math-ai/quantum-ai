import stim

def analyze():
    with open("stabilizers_155.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Total lines: {len(lines)}")
    
    # Categorize by first non-I character and length
    types = {}
    for line in lines:
        s = line.lstrip('I')
        pattern = s[:5] # heuristic
        if pattern not in types:
            types[pattern] = 0
        types[pattern] += 1
        
    for k, v in types.items():
        print(f"Pattern starts with {k}: {v}")

    # Check length of strings
    lengths = set(len(line) for line in lines)
    print(f"Lengths found: {lengths}")
    if len(lengths) == 1:
        print(f"All length {list(lengths)[0]}")

if __name__ == "__main__":
    analyze()
