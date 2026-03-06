stabs = [
    "XZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZXI",
    "IXZZXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIXZZXIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIXZZXIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXZZXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXZZXIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIXZZXIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXZZX",
    "XIXZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIXIXZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIXIXZZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIXIXZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIXIXZZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXZZ",
    "ZXIXZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIZXIXZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIZXIXZIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZXIXZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIZXIXZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIZXIXZIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZXIXZ",
    "IIIIIIIIIIXXXXXIIIIIXXXXXXXXXXXXXXX",
    "IIIIIXXXXXIIIIIXXXXXIIIIIXXXXXXXXXX",
    "XXXXXXXXXXXXXXIIIIIIIIIIXXXXXIIIII",
    "IIIIIIIIIIZZZZZIIIIIZZZZZZZZZZZZZZZ",
    "IIIIIZZZZZIIIIIZZZZZIIIIIZZZZZZZZZZ",
    "ZZZZZZZZZZZZZZZIIIIIIIIIIZZZZZIIIII"
]

print(f"Stab 30 orig: {stabs[30]}")
print(f"Length: {len(stabs[30])}")
print(f"Stab 33 orig: {stabs[33]}")
print(f"Length: {len(stabs[33])}")

# Try adding an X to make it 35
stab30_fixed = "X" + stabs[30]
print(f"Stab 30 fixed A (prepend X): {stab30_fixed} (Len {len(stab30_fixed)})")

# Try appending X? No, check Z counterpart
# Z counterpart is ZZZZZZZZZZZZZZZIIIIIIIIIIZZZZZIIIII (15 Zs at start)
# S30 is XXXXXXXXXXXXXXIIIIIIIIIIXXXXXIIIII (14 Xs at start)
# So it is missing one X at the beginning.

stab30_fixed = "X" + stabs[30]
if len(stab30_fixed) == 35:
    print("Fix looks correct based on symmetry with Z stabilizer.")
    stabs[30] = stab30_fixed

# Check lengths again
for i, s in enumerate(stabs):
    if len(s) != 35:
        print(f"Index {i} still has bad length {len(s)}")

# Check commutativity with the fix
import numpy as np

def check_commutativity(stabs):
    n = len(stabs[0])
    k = len(stabs)
    
    def pauli_to_vector(p):
        if p == 'I': return 0, 0
        if p == 'X': return 1, 0
        if p == 'Z': return 0, 1
        if p == 'Y': return 1, 1
        raise ValueError(f"Invalid Pauli: {p}")

    xs = np.zeros((k, n), dtype=int)
    zs = np.zeros((k, n), dtype=int)

    for i, s in enumerate(stabs):
        for j, char in enumerate(s):
            x, z = pauli_to_vector(char)
            xs[i, j] = x
            zs[i, j] = z

    comm_matrix = (xs @ zs.T + zs @ xs.T) % 2
    return comm_matrix

comm = check_commutativity(stabs)
anticommuting_pairs = []
for i in range(len(stabs)):
    for j in range(i + 1, len(stabs)):
        if comm[i, j] == 1:
            anticommuting_pairs.append((i, j))

print(f"Anticommuting pairs with fix: {len(anticommuting_pairs)}")
if anticommuting_pairs:
    print("Pairs:", anticommuting_pairs)

# Save the corrected stabilizers
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_35_corrected.txt", "w") as f:
    for s in stabs:
        f.write(s + "\n")
