s6 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX"
s34 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ"

# Align from the start
for i in range(len(s6)):
    c6 = s6[i]
    c34 = s34[i]
    if c6 != 'I' or c34 != 'I':
        print(f"Index {i}: {c6} vs {c34}")

import stim
p6 = stim.PauliString(s6)
p34 = stim.PauliString(s34)
print(f"Commutes: {p6.commutes(p34)}")
