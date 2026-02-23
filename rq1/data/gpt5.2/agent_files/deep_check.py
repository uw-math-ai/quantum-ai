from solve_119 import stabilizers
import stim

# Re-check length of 34
s34 = stabilizers[34]
print(f"Len 34: {len(s34)}")
# Print explicitly
print(f"Str 34: '{s34}'")

# Check 6
s6 = stabilizers[6]
print(f"Len 6: {len(s6)}")
print(f"Str 6: '{s6}'")

# Check 62
s62 = stabilizers[62]
print(f"Len 62: {len(s62)}")
print(f"Str 62: '{s62}'")

# Check 90
s90 = stabilizers[90]
print(f"Len 90: {len(s90)}")
print(f"Str 90: '{s90}'")

# Check 112
# Wait, index 112? There are 118 stabilizers. Index 117 is the last one.
# So index 112 is valid.
s112 = stabilizers[112]
print(f"Len 112: {len(s112)}")
print(f"Str 112: '{s112}'")

# Check their commutation with others
# Specifically checking why they failed.
# Failure means the generated state is NOT +1 eigenstate.
# This implies the stabilizer is NOT in the stabilizer group of the generated state.
# But the state was generated FROM these stabilizers using elimination.
# So it should be impossible unless:
# 1. The elimination failed (but it didn't throw error).
# 2. The stabilizers are redundant/dependent in a way that Stim dropped some.
# 3. The input to Stim had anticommuting checks that were ignored or resolved arbitrarily?
# Stim raises error on anticommuting. I saw that before.
# Then I ran again, and it SUCCEEDED.
# This means AFTER fixing s62 length, they COMMUTE!

# So if they commute, and we generate a state from them, that state MUST satisfy them.
# Unless I am using `allow_redundant=True` and some are contradictory?
# But contradictory means anticommuting.

# Let's check commutation of ALL pairs again.
ps = [stim.PauliString(s) for s in stabilizers]
problem = False
for i in range(len(ps)):
    for j in range(i+1, len(ps)):
        if not ps[i].commutes(ps[j]):
            print(f"Anticommute: {i} vs {j}")
            problem = True
if not problem:
    print("All commute.")
