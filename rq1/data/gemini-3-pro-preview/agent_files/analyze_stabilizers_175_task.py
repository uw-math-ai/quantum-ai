import numpy as np

def pauli_to_binary(p_str):
    n = len(p_str)
    x = np.zeros(n, dtype=int)
    z = np.zeros(n, dtype=int)
    for i, c in enumerate(p_str):
        if c == 'X':
            x[i] = 1
        elif c == 'Z':
            z[i] = 1
        elif c == 'Y':
            x[i] = 1
            z[i] = 1
    return x, z

def symplectic_product(x1, z1, x2, z2):
    return np.sum(x1 * z2 + z1 * x2) % 2

def check_commutativity(stabilizers):
    n = len(stabilizers)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            x1, z1 = pauli_to_binary(stabilizers[i])
            x2, z2 = pauli_to_binary(stabilizers[j])
            if symplectic_product(x1, z1, x2, z2) != 0:
                anticommuting_pairs.append((i, j))
    return anticommuting_pairs

with open('data/gemini-3-pro-preview/agent_files/stabilizers_175_task.txt', 'r') as f:
    stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]

print(f"Number of stabilizers: {len(stabilizers)}")
print(f"Length of first stabilizer: {len(stabilizers[0])}")

# Check lengths
lengths = [len(s) for s in stabilizers]
unique_lengths = set(lengths)
if len(unique_lengths) > 1:
    print(f"Stabilizers have different lengths: {unique_lengths}")
    for i, s in enumerate(stabilizers):
        if len(s) != 175:
            print(f"Stabilizer {i} has length {len(s)}")
            print(f"  Prev: {stabilizers[i-1]}")
            print(f"  Curr: {s}")
            print(f"  Next: {stabilizers[i+1]}")
            
anticommuting = check_commutativity(stabilizers)
if not anticommuting:
    print("All stabilizers commute.")
else:
    print(f"Found {len(anticommuting)} anticommuting pairs.")
    for i, j in anticommuting[:10]:
        print(f"  {i} and {j} anticommute")
if not anticommuting:
    print("All stabilizers commute.")
else:
    print(f"Found {len(anticommuting)} anticommuting pairs.")
    for i, j in anticommuting[:10]:
        print(f"  {i} and {j} anticommute")
        
# Check for duplicates
unique_stabs = set(stabilizers)
if len(unique_stabs) != len(stabilizers):
    print(f"Warning: {len(stabilizers) - len(unique_stabs)} duplicate stabilizers found.")
    seen = set()
    duplicates = []
    for s in stabilizers:
        if s in seen:
            duplicates.append(s)
        seen.add(s)
    print(f"First duplicate: {duplicates[0]}")
    # find indices
    for dup in duplicates[:3]:
        indices = [i for i, x in enumerate(stabilizers) if x == dup]
        print(f"Duplicate found at indices: {indices}")
