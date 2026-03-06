import numpy as np

stabilizers = [
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

    # Commutativity check: simple symplectic inner product
    # two pauli strings commute if they anticommute an even number of times
    # XZ = -ZX (anticommute)
    # XY = -YX (anticommute)
    # YZ = -ZY (anticommute)
    # A pair (x1, z1) and (x2, z2) anticommutes if x1*z2 + z1*x2 = 1 (mod 2)
    
    comm_matrix = (xs @ zs.T + zs @ xs.T) % 2
    return comm_matrix

comm = check_commutativity(stabilizers)
anticommuting_pairs = []
for i in range(len(stabilizers)):
    for j in range(i + 1, len(stabilizers)):
        if comm[i, j] == 1:
            anticommuting_pairs.append((i, j))

print(f"Number of stabilizers: {len(stabilizers)}")
print(f"Number of qubits: {len(stabilizers[0])}")
print(f"Anticommuting pairs: {len(anticommuting_pairs)}")

if anticommuting_pairs:
    print("First 10 pairs:", anticommuting_pairs[:10])
else:
    print("All stabilizers commute.")

# Save stabilizers to a file for potential use by other scripts
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_35_task.txt", "w") as f:
    for s in stabilizers:
        f.write(s + "\n")
