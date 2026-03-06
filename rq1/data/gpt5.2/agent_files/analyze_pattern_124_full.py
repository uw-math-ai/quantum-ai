import stim

# Use relative path if script is in same dir
with open("stabilizers_124.txt", "r") as f:
    stabilizers = [l.strip() for l in f.readlines() if l.strip()]

def find_indices(s):
    return [i for i, c in enumerate(s) if c != 'I']

def print_pattern(idx):
    if idx >= len(stabilizers): return
    s = stabilizers[idx]
    indices = find_indices(s)
    chars = [s[i] for i in indices]
    print(f"S{idx}: Indices {indices}, Chars {chars}")

print(f"Total stabilizers: {len(stabilizers)}")

print("Checking pattern for S16 and surroundings:")
for i in range(12, 24):
    print_pattern(i)

print("\nChecking Z stabilizers pattern around S116:")
# S116 is Index 116.
# Let's check 112-122
for i in range(112, 122):
    print_pattern(i)

# Also check 87 and 90 just in case
print("\nChecking S87 and S90:")
print_pattern(87)
print_pattern(90)
