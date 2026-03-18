def check_lengths():
    with open("target_stabilizers_rq3_fresh.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    cleaned_lines = []
    for line in lines:
        parts = line.split(',')
        for p in parts:
            if p.strip():
                cleaned_lines.append(p.strip())
                
    print(f"Number of stabilizers: {len(cleaned_lines)}")
    lengths = [len(s) for s in cleaned_lines]
    print(f"Max length: {max(lengths)}")
    print(f"Min length: {min(lengths)}")
    
    max_qubit_used = -1
    for s in cleaned_lines:
        for i, char in enumerate(s):
            if char in "XYZ":
                max_qubit_used = max(max_qubit_used, i)
    
    print(f"Max qubit index used (0-based): {max_qubit_used}")
    
    for i, s in enumerate(cleaned_lines):
        if len(s) > 42:
            print(f"Stabilizer {i} has length {len(s)}: {s}")

if __name__ == "__main__":
    check_lengths()
