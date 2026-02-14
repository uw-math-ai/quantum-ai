
import numpy as np

# Local stabilizers for a 9-qubit block
# Block indices: 0..8
local_stabs = [
    ([0, 1, 3, 4], 'X'),
    ([4, 5, 7, 8], 'X'),
    ([2, 5], 'X'),
    ([3, 6], 'X'),
    ([3, 4, 6, 7], 'Z'),
    ([1, 2, 4, 5], 'Z'),
    ([0, 1], 'Z'),
    ([7, 8], 'Z')
]

# Let's verify commutation of these 8 stabilizers.
def commute(stab1, stab2):
    idx1, type1 = stab1
    idx2, type2 = stab2
    if type1 == type2:
        return True
    # Count overlap
    overlap = len(set(idx1) & set(idx2))
    return overlap % 2 == 0

for i in range(len(local_stabs)):
    for j in range(i+1, len(local_stabs)):
        if not commute(local_stabs[i], local_stabs[j]):
            print(f"Non-commuting: {i} and {j}")

# Find logical operators for this 9-qubit block.
# They must commute with all local stabs.
# One pair of logical X and Z.
# Let's search brute force or guess.
# Maybe Z_L = Z0 Z1 ... Z8? Or X_L = X0 ... X8?
# Or maybe simpler?

def is_commute_op(op_idx, op_type, stabs):
    # op_idx: list of indices
    # op_type: 'X' or 'Z'
    for s_idx, s_type in stabs:
        if s_type != op_type:
            overlap = len(set(op_idx) & set(s_idx))
            if overlap % 2 != 0:
                return False
    return True

# Search for single-qubit logical operators?
for i in range(9):
    if is_commute_op([i], 'X', local_stabs):
        print(f"Found logical X candidate: X({i})")
    if is_commute_op([i], 'Z', local_stabs):
        print(f"Found logical Z candidate: Z({i})")

# Search for 3-qubit logical operators
import itertools
for i in itertools.combinations(range(9), 3):
    if is_commute_op(list(i), 'X', local_stabs):
        print(f"Found logical X candidate: X{i}")
        break # Just one
for i in itertools.combinations(range(9), 3):
    if is_commute_op(list(i), 'Z', local_stabs):
        print(f"Found logical Z candidate: Z{i}")
        break

