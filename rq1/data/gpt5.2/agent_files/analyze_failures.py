import stim
from solve_119 import stabilizers

# Indices of failed stabilizers
failed_indices = [6, 34, 62, 90, 112] # 112 based on count from end? No let's find them.

failed_stabs = [
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIIXIXXIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXIXXIIIIX",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIIIZIZZIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZZIZZIIIIZ",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZIIIIIIIIIIZII"
]

# Check if these are in the stabilizers list
for s in failed_stabs:
    found = False
    for i, orig in enumerate(stabilizers):
        if s == orig:
            print(f"Failed stab found at index {i}")
            found = True
            break
    if not found:
        print(f"Failed stab NOT found in original list: {s[:10]}...")

# Check commutation of these with others
ps = [stim.PauliString(s) for s in stabilizers]
for i in [6, 34, 62, 90, 112]:
    if i < len(ps):
        print(f"Checking commutation for index {i}")
        for j in range(len(ps)):
            if not ps[i].commutes(ps[j]):
                print(f"  Anticommutes with {j}")

