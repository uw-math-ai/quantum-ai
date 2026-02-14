import stim

# Define the single-block stabilizers for one 19-qubit block
block_stabs = [
    "IIXIIXIIXXIIIIIIIII",
    "IIIIIIIIIIXIXIIIIXX",
    "IIIIIIIIIIXXIXIIIIX",
    "XXIIIIIIIIIIIIXXIII",
    "XXIXXIXIIIIIIIIIXII",
    "IIXIXIIIXIIIIIIIXII",
    "IXIIIIXXIIIIIIIXIII",
    "IIIXIIXXIIXXXIIIIII",
    "IIIXXIIIXXIXIXIIIII",
    "IIZIIZIIZZIIIIIIIII",
    "IIIIIIIIIIZIZIIIIZZ",
    "IIIIIIIIIIZZIZIIIIZ",
    "ZZIIIIIIIIIIIIZZIII",
    "ZZIZZIZIIIIIIIIIZII",
    "IIZIZIIIZIIIIIIIZII",
    "IZIIIIZZIIIIIIIZIII",
    "IIIZIIZZIIZZZIIIIII",
    "IIIZZIIIZZIZIZIIIII"
]

# We need to find a state that satisfies these.
# This is a code on 19 qubits with 18 stabilizers. It encodes 1 logical qubit.
# To fix the state of the block, we can choose an arbitrary logical operator, say Z_L, and set it to +1.
# Or we can just find *any* state satisfying these.
# But wait, the global stabilizers (72 and 73) impose constraints on the logical operators of the blocks.

# Let X_global = X_B0 * X_B1 * X_B2 * X_B3
# Let Z_global = Z_B0 * Z_B1 * Z_B2 * Z_B3
# where X_Bi is the pattern IIIIXXXXXIIIIIIIIII on block i.
# And Z_Bi is the pattern IIIIZZZZZIIIIIIIIII on block i.

# We need the state to be +1 eigenstate of X_global and Z_global.
# This means the product of the measurement results of X_Bi on each block must be +1.
# And same for Z_Bi.

# Let's verify if X_Bi and Z_Bi commute with the block stabilizers.
# If they do, they are logical operators (or stabilizers) of the block code.

def commute(p1, p2):
    anti = False
    for c1, c2 in zip(p1, p2):
        if c1 != 'I' and c2 != 'I' and c1 != c2:
            anti = not anti
    return anti

X_Bi = "IIIIXXXXXIIIIIIIIII"
Z_Bi = "IIIIZZZZZIIIIIIIIII"

print("Checking commutation with block stabilizers:")
for i, s in enumerate(block_stabs):
    if commute(s, X_Bi):
        print(f"X_Bi anti-commutes with stabilizer {i}: {s}")
    if commute(s, Z_Bi):
        print(f"Z_Bi anti-commutes with stabilizer {i}: {s}")

# Check if X_Bi and Z_Bi commute with each other
if commute(X_Bi, Z_Bi):
    print("X_Bi and Z_Bi anti-commute")
else:
    print("X_Bi and Z_Bi commute")

# Construct the Tableau for the single block
t = stim.Tableau.from_conjugated_generators(
    xs=[], 
    zs=[], 
    # We can't use from_conjugated_generators easily with strings directly unless we map them.
    # But we can use Gaussian elimination.
)

# Let's use a simple Gaussian elimination script to find a circuit for the block.
# We will find a circuit that prepares the +1 eigenstate of the 18 stabilizers.
# This will leave 1 degree of freedom (logical qubit).
# We need to characterize the logical operators on this block.
