def check_shift(s1, s2):
    common = 0
    for i in range(min(len(s1), len(s2))-1):
        if s1[i+1] == s2[i]:
            common += 1
    print(f"Match shift: {common}/{min(len(s1), len(s2))-1}")

stabilizers = [
    "IXIIXIIXXXXXIIIIIIIIIIX",
    "XIIXIIXXXXXIIIIIIIIIIXI",
    "IXXIXXXIIIXXIIIIIIIIXII",
    "XXIXXXIIIXXIIIIIIIIXIII",
    "XXXXIIXIIXXIIIIIIXIIII", # The problematic one
    "XIXIXIXXXIIXIIIIIXIIIII"
]

print("S0 vs S1")
check_shift(stabilizers[0], stabilizers[1])
print("S2 vs S3")
check_shift(stabilizers[2], stabilizers[3])
print("S4 vs S5")
# S4 is length 22, S5 is length 23.
# Maybe S4 is a shift of something or S5 is a shift of S4?
# Or maybe S4 is missing a char?

print("S4 raw: ", stabilizers[4])
print("S5 raw: ", stabilizers[5])
