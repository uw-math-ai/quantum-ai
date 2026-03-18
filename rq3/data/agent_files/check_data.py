with open("my_stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Number of stabilizers: {len(lines)}")
print(f"Length of first stabilizer: {len(lines[0])}")
print(f"First stabilizer: {lines[0]}")
print(f"Last stabilizer: {lines[-1]}")

with open("my_baseline.stim", "r") as f:
    content = f.read()
    # Find max qubit index
    import re
    indices = [int(x) for x in re.findall(r'\d+', content)]
    print(f"Max qubit index in baseline: {max(indices)}")
