import stim

def analyze():
    with open('stabilizers_90.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = []
    for i, line in enumerate(lines):
        if len(line) != 90:
             print(f"Line {i+1}: length {len(line)}")
        try:
            s = stim.PauliString(line)
            stabilizers.append(s)
            if len(s) != 90:
                print(f"Stabilizer {i} has length {len(s)}")
        except Exception as e:
            print(f"Error parsing stabilizer {i}: {e}")

    print(f"Parsed {len(stabilizers)} stabilizers.")
    
    # Check 0 and 60 specifically
    if len(stabilizers) > 60:
        s0 = stabilizers[0]
        s60 = stabilizers[60]
        print(f"S0: {s0}")
        print(f"S60: {s60}")
        print(f"Commutes: {s0.commutes(s60)}")
        
        # Manually check overlap
        for k in range(len(s0)):
            p0 = s0[k]
            p60 = s60[k]
            if p0 != 0 and p60 != 0:
                print(f"Index {k}: S0={p0}, S60={p60}")

    # Count anti-commuting pairs
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                anticommuting_pairs.append((i, j))

    print(f"Found {len(anticommuting_pairs)} anti-commuting pairs.")
    if len(anticommuting_pairs) > 0:
        print("First 10 pairs:", anticommuting_pairs[:10])

if __name__ == "__main__":
    analyze()
