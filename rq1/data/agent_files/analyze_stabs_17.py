import numpy as np
import stim

# Generators provided in the prompt
x_gens = [
    "IIIIIXIIIXIXXIIII",
    "IIIIIIIIXIXIIXIXI",
    "IIIXIIIXIIIIIIXIX",
    "IIXIIIXIIIIIIIXIX",
    "IIIIXXXXXIXXIIIIX",
    "IXIIXIIIIIXIIXIII",
    "IIIIIIIIXXIXIIIXI",
    "XIXXIIIIIIIIIIXII"
]

z_gens = [
    "IIIIIZIIIZIZZIIII",
    "IIIIIIIIZIZIIZIZI",
    "IIIZIIIZIIIIIIZIZ",
    "IIZIIIZIIIIIIIZIZ",
    "IIIIZZZZZIZZIIIIZ",
    "IZIIZIIIIIZIIZIII",
    "IIIIIIIIZZIZIIIZI",
    "ZIZZIIIIIIIIIIZII"
]

all_gens = x_gens + z_gens
n_qubits = len(x_gens[0])
print(f"Number of qubits: {n_qubits}")
print(f"Number of X generators: {len(x_gens)}")
print(f"Number of Z generators: {len(z_gens)}")

def check_commutation(gens):
    n = len(gens[0])
    m = len(gens)
    commutes = True
    for i in range(m):
        for j in range(i+1, m):
            g1 = gens[i]
            g2 = gens[j]
            anticommutes = 0
            for k in range(n):
                p1 = g1[k]
                p2 = g2[k]
                if p1 != 'I' and p2 != 'I' and p1 != p2:
                    anticommutes += 1
            if anticommutes % 2 != 0:
                print(f"Generator {i} and {j} anticommute!")
                commutes = False
    return commutes

print(f"All generators commute: {check_commutation(all_gens)}")

# Check if X and Z generators correspond to the same parity check matrix
# (i.e. is it a CSS code defined by a single matrix H_x = H_z?)
# Let's extract the binary matrix for X and Z.

def to_binary(gens, type_char):
    mat = []
    for g in gens:
        row = [1 if c == type_char else 0 for c in g]
        mat.append(row)
    return np.array(mat)

Hx = to_binary(x_gens, 'X')
Hz = to_binary(z_gens, 'Z')

print("Hx matrix:")
print(Hx)
print("Hz matrix:")
print(Hz)

if np.array_equal(Hx, Hz):
    print("Hx is identical to Hz. This is a CSS code with Hx = Hz.")
else:
    print("Hx is NOT identical to Hz.")
