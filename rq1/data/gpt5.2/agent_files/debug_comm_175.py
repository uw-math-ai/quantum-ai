import stim

s2 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
s105 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"

p2 = stim.PauliString(s2)
p105 = stim.PauliString(s105)

print(f"s2 length: {len(s2)}")
print(f"s105 length: {len(s105)}")
print(f"Commutes: {p2.commutes(p105)}")

# Check indices
for i in range(len(s2)):
    c1 = s2[i]
    c2 = s105[i]
    if c1 != 'I' and c2 != 'I':
        commutes_local = (c1 == c2) or (c1 == 'I') or (c2 == 'I')
        print(f"Index {i}: {c1} vs {c2} -> {'Commutes' if commutes_local else 'Anticommutes'}")
