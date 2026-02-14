import stim
import numpy as np

stabilizers_str = [
    "XXXXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXXXXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXXXXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXXXXIIIIIII",
    "IXXIXXIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXXIXXIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIXXIXXIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIXXIXXII",
    "IIXXIXXIIXXXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIXXIXXIIXXXIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIXXXIXIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIXXXIXI",
    "IIIIXXXXIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIXXXXIIIXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIXXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIXXXX",
    "ZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIII",
    "IZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIII",
    "IIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIZZIIIIIIII",
    "IIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIII",
    "IZIIZIIIZIIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZIIZIIIZIIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIZIIIZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIZIIIZII",
    "IIZIIZIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZIIZIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIZIZIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIZIZIII",
    "IIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIII",
    "IIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZII",
    "IIIIIZZIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIZZIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIZIZIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIZIZI",
    "IIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZ",
    "XXXXIIIIXXXIIIIXXXXIIIIXXXIIIIXXXXIIIIXXXIIIIXXXXIIIIXXXIIII",
    "ZZIIIIIIZIIIIIIZZIIIIIIZIIIIIIZZIIIIIIZIIIIIIZZIIIIIIZIIIIII"
]

failed_stab_idx = 55
failed_stab = stabilizers_str[failed_stab_idx]
print(f"Failed Stabilizer: {failed_stab}")

ps = [stim.PauliString(s) for s in stabilizers_str]

# Check if failed_stab is a product of others.
# If so, check if the sign matches.
# We can do this by forming a matrix of the others and Gaussian elimination.

def pauli_to_vec(p):
    # n qubits -> 2n bits
    # z[i] x[i]
    # actually Stim uses x, z convention usually? No, the order depends.
    # We just need consistent mapping.
    # Let's map X->(1,0), Z->(0,1), Y->(1,1), I->(0,0)
    # So 2N bits.
    n = len(p)
    v = np.zeros(2*n, dtype=int)
    # Check Stim documentation or just iterate.
    # p is stim.PauliString
    # We can iterate over qubits.
    # Or use p.to_numpy().
    # p.to_numpy() returns (xs, zs) where xs and zs are bool arrays.
    # Wait, in recent versions it might return something else.
    # Let's try explicit loop just in case.
    for k in range(n):
        c = p[k] # returns 0,1,2,3 for I,X,Y,Z
        # X=1, Y=2, Z=3
        if c == 1: # X
            v[k] = 1
        elif c == 3: # Z
            v[n+k] = 1
        elif c == 2: # Y
            v[k] = 1
            v[n+k] = 1
    return v

# Build matrix of all others
matrix = []
for i, p in enumerate(ps):
    v = pauli_to_vec(p)
    if i == failed_stab_idx:
        continue
    if len(v) != 120:
        print(f"Warning: Stabilizer {i} has length {len(v)/2}: {stabilizers_str[i]}")
    matrix.append(v)
    
    # Check length
    # print(len(pauli_to_vec(p)))
    
target = pauli_to_vec(ps[failed_stab_idx])

# Use GF(2) elimination
# We can use scipy or simple numpy implementation (slow but fine for 60x120)
# Or simple python implementation.

# A simple Gaussian elimination
# matrix is M x 2N
# target is 1 x 2N
# Solve x * M = target

m = np.array(matrix, dtype=int)
t = np.array(target, dtype=int)

# Transpose to solve M^T * x = target^T (Wait, x is coefficients of rows)
# Yes, x * M = t => M^T * x^T = t^T
# We want to find x.

# Let's augment M^T with t^T
augmented = np.vstack([m, t]) # No, we want to see if t is in span of rows of m.
# So rank(m) should be same as rank([m; t])

rank_m = np.linalg.matrix_rank(m) # Wait, this is over Reals, not GF(2).
# Need GF(2) rank.

def gf2_rank(rows):
    rows = list(rows)
    pivot_row = 0
    num_rows = len(rows)
    num_cols = len(rows[0])
    
    for col in range(num_cols):
        if pivot_row >= num_rows:
            break
        
        # Find a row with 1 in this column
        for i in range(pivot_row, num_rows):
            if rows[i][col] == 1:
                # Swap
                rows[i], rows[pivot_row] = rows[pivot_row], rows[i]
                break
        else:
            continue
            
        # Eliminate
        for i in range(num_rows):
            if i != pivot_row and rows[i][col] == 1:
                rows[i] = (rows[i] + rows[pivot_row]) % 2
                
        pivot_row += 1
        
    # Count non-zero rows
    r = 0
    for row in rows:
        if np.any(row):
            r += 1
    return r

r_m = gf2_rank(m.copy())
r_aug = gf2_rank(np.vstack([m, t]).copy())

print(f"Rank of others: {r_m}")
print(f"Rank of others + target: {r_aug}")

if r_m == r_aug:
    print("Target IS linearly dependent on others.")
else:
    print("Target is independent.")

# If dependent, we need to check the sign.
# To check sign, we need the coefficients x such that x * M = t.
# This is harder to get from simple rank, need full solver.
# But if it is dependent, and check_stabilizers_tool failed, it means the sign is wrong.
# i.e. Product(others) = -Target.
# This implies inconsistency in the input.
# Or `stim` made a choice for "others" that contradicts "Target".
# But `stim` should detect inconsistency.
# UNLESS `stim` just ignores the target if it's redundant and doesn't check sign?
# If `allow_redundant=True` is used, `stim` might pick a basis and ignore the rest?
# The doc says "It is an error to provide contradictory stabilizers".
# So `stim` *should* check.

# Let's check dependency first.
