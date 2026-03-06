with open("stabilizers_186.txt", "r") as f:
    lines = [line.strip() for line in f]

s105 = lines[105]
print(f"S105: {s105}")
print(f"Length: {len(s105)}")

# Compare with S104 and S106 to see the pattern
print(f"S104: {lines[104]}")
print(f"S106: {lines[106]}")
