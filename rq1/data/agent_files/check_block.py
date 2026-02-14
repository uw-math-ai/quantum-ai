import stim

# Define the generators for a single block
gens = [
    "XZZXI",
    "IXZZX",
    "XIXZZ",
    "ZXIXZ"
]

# Check commutation
def commutes(s1, s2):
    n = len(s1)
    anti = 0
    for i in range(n):
        if s1[i] != 'I' and s2[i] != 'I' and s1[i] != s2[i]:
            anti += 1
    return anti % 2 == 0

print("Commutation check:")
for i in range(4):
    for j in range(i+1, 4):
        c = commutes(gens[i], gens[j])
        print(f"[{i}, {j}]: {c}")

# If they commute, they stabilize a 2D subspace (1 logical qubit).
# Let's find the logical operators for this block.
# Logical X and Z.
# Logical X usually XXXXX or ZZZZZ?

print("\nLogical operators candidates:")
candidates = ["XXXXX", "ZZZZZ"]
for cand in candidates:
    commutes_all = True
    for g in gens:
        if not commutes(cand, g):
            commutes_all = False
            break
    print(f"{cand}: commutes with all? {commutes_all}")

