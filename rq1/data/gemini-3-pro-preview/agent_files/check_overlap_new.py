import stim

def check_overlap(i, j):
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    s1 = lines[i]
    s2 = lines[j]
    
    print(f"Line {i} length: {len(s1)}")
    print(f"Line {j} length: {len(s2)}")
    
    if len(s1) > 131:
        print(f"Index 131 in line {i}: {s1[131]}")
    if len(s2) > 131:
        print(f"Index 131 in line {j}: {s2[131]}")

    xs = [k for k, c in enumerate(s1) if c == 'X']
    print(f"Xs in line {i}: {xs}")
    
    zs = [k for k, c in enumerate(s2) if c == 'Z']
    print(f"Zs in line {j}: {zs}")
    
if __name__ == "__main__":
    check_overlap(34, 79)
