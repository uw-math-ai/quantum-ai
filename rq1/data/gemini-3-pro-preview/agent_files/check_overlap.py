s8 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
s92 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIIIIZZIIIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"

print(f"Indices 8: {[i for i, c in enumerate(s8) if c != 'I']}")
print(f"Indices 92: {[i for i, c in enumerate(s92) if c != 'I']}")

overlap = []
for i in range(len(s8)):
    if s8[i] != 'I' and s92[i] != 'I':
        overlap.append(i)
        
print(f"Overlap: {overlap}")
