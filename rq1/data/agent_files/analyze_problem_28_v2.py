import stim
import numpy as np
import galois

stabilizers = [
    "IIXIXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXIXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXIXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXIXXX",
    "IXIXIXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIXIXIXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXIXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIXIXIXX",
    "XXXIIXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXIIXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXIIXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXIIXI",
    "IIZIZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZIZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZIZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZIZZZ",
    "IZIZIZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIZIZIZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZIZIZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIZIZIZZ",
    "ZZZIIZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZIIZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZIIZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZIIZI",
    "XXIXIIIXXIXIIIXXIXIIIXXIXIII",
    "ZZIZIIIZZIZIIIZZIZIIIZZIZIII"
]

num_qubits = 28
num_stabilizers = len(stabilizers)

def str_to_pauli(s):
    xs = [1 if c in 'XY' else 0 for c in s]
    zs = [1 if c in 'ZY' else 0 for c in s]
    return xs, zs

xs_matrix = []
zs_matrix = []

for s in stabilizers:
    x, z = str_to_pauli(s)
    xs_matrix.append(x)
    zs_matrix.append(z)

xs = np.array(xs_matrix, dtype=int)
zs = np.array(zs_matrix, dtype=int)

GF2 = galois.GF(2)
tableau = GF2(np.concatenate((xs, zs), axis=1))
rank = np.linalg.matrix_rank(tableau)
print(f"Rank: {rank}")
print(f"Num stabilizers: {num_stabilizers}")

# Check commutation
def check_commutation(xs, zs):
    n = xs.shape[0]
    for i in range(n):
        for j in range(i+1, n):
            c = np.sum(xs[i] * zs[j] + zs[i] * xs[j]) % 2
            if c != 0:
                print(f"Non-commuting: {i} and {j}")
                return False
    return True

if check_commutation(xs, zs):
    print("All commute.")
else:
    print("Some do not commute.")

# Since rank is 26 (likely), we need to fill it up to 28 for a full stabilizer state,
# or just find a state that satisfies these 26.
# A simple way is to extend the set to 28 commuting stabilizers and use Gaussian elimination.
