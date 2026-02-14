import stim
import numpy as np
from ldpc import mod2

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

def to_binary(gens, type_char):
    mat = []
    for g in gens:
        row = [1 if c == type_char else 0 for c in g]
        mat.append(row)
    return np.array(mat, dtype=int)

Hx = to_binary(x_gens, 'X')
Hz = to_binary(z_gens, 'Z')

ker_Hx = mod2.nullspace(Hx)
ker_Hz = mod2.nullspace(Hz)

print(f"Hx shape: {Hx.shape}")
print(f"Hz shape: {Hz.shape}")
print(f"ker_Hx type: {type(ker_Hx)}")
print(f"ker_Hx shape: {ker_Hx.shape}")

# Check `mod2.rank` behavior
test_v = ker_Hx[0]
print(f"Test vector type: {type(test_v)}")
print(f"Test vector shape: {test_v.shape}")

# If test_v is 2D (1, 17), vstack should work.
# If test_v is 1D (17,), vstack should work.
# But error suggests mismatch.

mat = np.vstack([Hz, test_v])
print(f"Stacked matrix shape: {mat.shape}")

rank = mod2.rank(mat)
print(f"Rank: {rank}")
