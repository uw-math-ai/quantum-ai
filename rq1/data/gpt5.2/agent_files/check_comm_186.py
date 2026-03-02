import stim

def check_comm():
    with open("stabilizers_186.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    stabs = [stim.PauliString(line) for line in lines]
    
    n = len(stabs)
    bad_pairs = []
    for i in range(n):
        for j in range(i+1, n):
            if not stabs[i].commutes(stabs[j]):
                bad_pairs.append((i, j))
                if len(bad_pairs) < 10:
                    print(f"Pair {i}, {j} anticommutes")
    
    print(f"Total anticommuting pairs: {len(bad_pairs)}")
    if len(bad_pairs) > 0:
        idx = bad_pairs[0][1] # likely 105
        print(f"Stabilizer {idx}: {stabs[idx]}")
        for p in bad_pairs:
            if p[1] == idx:
                other = p[0]
                print(f"Anticommutes with {other}: {stabs[other]}")

if __name__ == "__main__":
    check_comm()
