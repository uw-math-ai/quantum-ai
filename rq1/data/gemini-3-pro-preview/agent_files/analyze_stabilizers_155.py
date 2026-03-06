import stim
import sys

# Read stabilizers
with open(r'data\gemini-3-pro-preview\agent_files\stabilizers_155.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

# stabilizers = [stim.PauliString(line) for line in lines]
stabilizers_all = [stim.PauliString(line) for line in lines]
stabilizers = [s for i, s in enumerate(stabilizers_all) if i != 148]

n = len(stabilizers)

print(f"Loaded {n} stabilizers.")
for i in range(140, 154):
    first_non_i = -1
    for k in range(len(stabilizers_all[i])):
        if stabilizers_all[i][k] != 0: # 0 is I
            first_non_i = k
            break
    print(f"{i}: Start {first_non_i}, Length {len(stabilizers_all[i])}")
    print(f"  {stabilizers_all[i]}")

anticommuting_pairs = []

for i in range(n):
    for j in range(i + 1, n):
        if stabilizers[i].commutes(stabilizers[j]) == False:
            anticommuting_pairs.append((i, j))

print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
for i, j in anticommuting_pairs[:10]:
    print(f"({i}, {j})")
    print(f"  {stabilizers[i]}")
    print(f"  {stabilizers[j]}")

if len(anticommuting_pairs) > 0:
    print("Stabilizers are inconsistent.")
else:
    print("Stabilizers are consistent.")
