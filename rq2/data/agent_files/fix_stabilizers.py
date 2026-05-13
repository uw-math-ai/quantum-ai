import stim

stabilizers = []
with open('stabilizers.txt', 'r') as f:
    for line in f:
        if line.strip():
            stabilizers.append(stim.PauliString(line.strip()))

# Remove index 118
if len(stabilizers) > 118:
    print(f"Removing stabilizer 118: {stabilizers[118]}")
    stabilizers.pop(118)
else:
    print("Index 118 out of range.")

with open('stabilizers.txt', 'w') as f:
    for s in stabilizers:
        f.write(str(s) + '\n')

print(f"New stabilizer count: {len(stabilizers)}")
