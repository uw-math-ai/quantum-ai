import stim

# Read stabilizers
with open("agent_files/stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

paulis = [stim.PauliString(s) for s in lines]
print(f"Total stabilizers: {len(paulis)}")

# Check which ones anticommute
anticommute_pairs = []
for i in range(len(paulis)):
    for j in range(i+1, len(paulis)):
        if not paulis[i].commutes(paulis[j]):
            anticommute_pairs.append((i, j))

print(f"Number of anticommuting pairs: {len(anticommute_pairs)}")
for pair in anticommute_pairs[:10]:
    print(f"  {pair[0]} vs {pair[1]}")

# Show the anticommuting stabilizers
if anticommute_pairs:
    i, j = anticommute_pairs[0]
    print(f"\nStabilizer {i}: {lines[i]}")
    print(f"Stabilizer {j}: {lines[j]}")
