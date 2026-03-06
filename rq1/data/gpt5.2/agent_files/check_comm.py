import stim
from solve_119 import stabilizers

s1 = stabilizers[6]
s2 = stabilizers[62]

p1 = stim.PauliString(s1)
p2 = stim.PauliString(s2)

print(f"s1: {s1}")
print(f"s2: {s2}")
print(f"Commutes: {p1.commutes(p2)}")

# Check detailed commutation
cnt = 0
for k in range(len(s1)):
    c1 = s1[k]
    c2 = s2[k]
    if c1 != 'I' and c2 != 'I' and c1 != c2:
        print(f"Index {k}: {c1} vs {c2}")
        cnt += 1
print(f"Anticommuting pairs: {cnt}")
