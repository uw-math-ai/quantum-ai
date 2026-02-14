
gen4_bad = "XXXXIIXIIXXIIIIIIXIIII"
gen15 = "ZZZZIIIZIIZZIIIIIIZIIII"

# Try inserting 'I' at index 6
gen4_fixed = gen4_bad[:6] + "I" + gen4_bad[6:]
print(f"Original Gen 4: {gen4_bad}")
print(f"Fixed Gen 4:    {gen4_fixed}")
print(f"Gen 15:         {gen15}")

# Check pattern match (X vs Z)
match = True
for i in range(len(gen15)):
    c4 = gen4_fixed[i]
    c15 = gen15[i]
    if (c4 == 'I' and c15 != 'I') or (c4 != 'I' and c15 == 'I'):
        print(f"Mismatch at {i}: {c4} vs {c15}")
        match = False
if match:
    print("Pattern matches!")
