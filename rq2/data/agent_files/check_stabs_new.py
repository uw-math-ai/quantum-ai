import stim

stabilizers = []
with open('stabilizers.txt', 'r') as f:
    for line in f:
        if line.strip():
            stabilizers.append(stim.PauliString(line.strip()))

print(f"Loaded {len(stabilizers)} stabilizers.")

bad_pairs = []
for i in range(len(stabilizers)):
    for j in range(i+1, len(stabilizers)):
        if not stim.PauliString.commutes(stabilizers[i], stabilizers[j]):
            bad_pairs.append((i, j))

print(f"Found {len(bad_pairs)} anti-commuting pairs.")
if bad_pairs:
    print("First 5 pairs:")
    for i, j in bad_pairs[:5]:
        print(f"{i}, {j}")
        print(f"S[{i}]: {stabilizers[i]}")
        print(f"S[{j}]: {stabilizers[j]}")
