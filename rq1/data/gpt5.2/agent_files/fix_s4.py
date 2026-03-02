stabilizers = [
    "IXIIXIIXXXXXIIIIIIIIIIX", # 0
    "XIIXIIXXXXXIIIIIIIIIIXI", # 1
    "IXXIXXXIIIXXIIIIIIIIXII", # 2
    "XXIXXXIIIXXIIIIIIIIXIII", # 3
    "XXXXIIXIIXXIIIIIIXIIII",  # 4 (short)
    "XIXIXIXXXIIXIIIIIXIIIII", # 5
    "IIIXXXXIXXIXIIIIXIIIIII", # 6
    "IIXXXXIXXIXIIIIXIIIIIII", # 7
    "IXXXXIXXIXIIIIXIIIIIIII", # 8
    "XXXXIXXIXIIIIXIIIIIIIII", # 9
    "XIXIIXIIXXXXXIIIIIIIIII", # 10
]

# Check S6->S7->S8->S9
# S6: IIIXXXXIXXIXIIIIXIIIIII
# S7: IIXXXXIXXIXIIIIXIIIIIII (Left shift of S6? No, Right shift?)
# S6 starts with III. S7 with II.
# S6 ends with IIIIII. S7 with IIIIIII.
# Looks like S6 is shifted LEFT to get S7?
# S6[1:] = IIXXXXIXXIXIIIIXIIIII
# S7[:-1] = IIXXXXIXXIXIIIIXIIIII
# Yes. S7 is S6 shifted LEFT.

# S8: IXXXXIXXIXIIIIXIIIIIIII
# S7[1:] = IXXXXIXXIXIIIIXIIIIII
# S8[:-1] = IXXXXIXXIXIIIIXIIIIII
# Yes. S8 is S7 shifted LEFT.

# S9: XXXXIXXIXIIIIXIIIIIIIII
# S8[1:] = XXXXIXXIXIIIIXIIIIIII
# S9[:-1] = XXXXIXXIXIIIIXIIIIIII
# Yes.

# So S6, S7, S8, S9 form a group.

# What about S4, S5?
# S5: XIXIXIXXXIIXIIIIIXIIIII
# S4: XXXXIIXIIXXIIIIIIXIIII
# If S4 is related to S5, maybe S5 is S4 shifted left?
# S4 (proposed): ?
# If S5 is S4 shifted left:
# S4[1:] == S5[:-1] ?
# S5[:-1] = XIXIXIXXXIIXIIIIIXIIII
# S4      = XXXXIIXIIXXIIIIIIXIIII
# Match? No.
# S4 starts with XXXX. S5 starts with XIXI.

# Maybe S4 relates to S3?
# S3: XXIXXXIIIXXIIIIIIIIXIII
# S4: XXXXIIXIIXXIIIIIIXIIII
# Maybe S4 is S3 shifted left?
# S3[1:] = XIXXXIIIXXIIIIIIIIIII
# S4[:-1] = XXXXIIXIIXXIIIIIIXIII
# No match.

# Let's look at S4 again.
# XXXXIIXIIXXIIIIIIXIIII
# Maybe it's missing an 'I' or 'X'.
# Length 22. Needs to be 23.
# Let's try inserting I or X at various positions and see if it commutes with S11.
# S11: IZIIZIIZZZZZIIIIIIIIIIZ
# S4 should commute with S11 (and others).

import stim

s11_str = "IZIIZIIZZZZZIIIIIIIIIIZ"
s4_short = "XXXXIIXIIXXIIIIIIXIIII"

candidates = []
for char in ['I', 'X', 'Z']:
    for pos in range(len(s4_short) + 1):
        new_s4 = s4_short[:pos] + char + s4_short[pos:]
        # Check commutation with s11
        if stim.PauliString(new_s4).commutes(stim.PauliString(s11_str)):
            # Also check if it makes sense with others?
            # Let's just collect commuting candidates
            candidates.append(new_s4)

print(f"Found {len(candidates)} candidates that commute with S11")
for c in candidates:
    print(c)
