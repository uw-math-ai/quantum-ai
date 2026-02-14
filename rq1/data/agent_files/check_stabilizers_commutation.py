import stim

def check_anticommutation(stabilizers):
    n = len(stabilizers)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                anticommuting_pairs.append((i, j))
    return anticommuting_pairs

try:
    with open("target_stabilizers.txt") as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    pairs = check_anticommutation(stabilizers)
    print(f"Found {len(pairs)} anticommuting pairs.")
    for i, j in pairs[:5]:
        print(f"Pair ({i}, {j}):")
        print(f"  {lines[i]}")
        print(f"  {lines[j]}")

except Exception as e:
    print(f"Error: {e}")
