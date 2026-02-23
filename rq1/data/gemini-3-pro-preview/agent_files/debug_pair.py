import stim

s8_str = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIXXIIII"
s62_str = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII"

print(f"Length S8: {len(s8_str)}")
print(f"Length S62: {len(s62_str)}")

p8 = stim.PauliString(s8_str)
p62 = stim.PauliString(s62_str)

print(f"P8: {p8}")
print(f"P62: {p62}")

print(f"Commutes: {p8.commutes(p62)}")

# Manual check
overlap = 0
for i in range(len(s8_str)):
    c1 = s8_str[i]
    c2 = s62_str[i]
    if c1 != 'I' and c2 != 'I' and c1 != c2:
        print(f"Anticommute at index {i}: {c1} vs {c2}")
        overlap += 1

print(f"Total anticommuting positions: {overlap}")
if overlap % 2 == 0:
    print("Should COMMUTE")
else:
    print("Should ANTICOMMUTE")
