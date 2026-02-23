import stim

def check_pair(i, j):
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    s1 = stim.PauliString(lines[i])
    s2 = stim.PauliString(lines[j])
    
    print(f"Stabilizer {i}: {s1}")
    print(f"Stabilizer {j}: {s2}")
    print(f"Commutes: {s1.commutes(s2)}")
    
    # Find where they anticommute
    for k in range(len(s1)):
        p1 = s1[k] # 0=I, 1=X, 2=Y, 3=Z
        p2 = s2[k]
        if p1 != 0 and p2 != 0 and p1 != p2:
            print(f"Index {k}: {p1} vs {p2} (anticommutes locally)")

if __name__ == "__main__":
    check_pair(34, 79)
