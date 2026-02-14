stabilizers = []

patterns = [
    "IIXIXXX",
    "IXIXIXX",
    "XXXIIXI",
    "IIZIZZZ",
    "IZIZIZZ",
    "ZZZIIZI"
]

# Each pattern is repeated 7 times, shifted by 7 positions
for pattern in patterns:
    for i in range(7):
        # Shift i*7
        prefix = "I" * (i * 7)
        suffix = "I" * (49 - (i * 7) - 7)
        stab = prefix + pattern + suffix
        stabilizers.append(stab)

# Add the extra stabilizers
extras = [
    "IIIIIIIIIIIIIIXXIXIIIIIIIIIIXXIXIIIXXIXIIIXXIXIII",
    "IIIIIIIXXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXIIIXXIXIII",
    "XXIXIIIXXIXIIIXXIXIIIIIIIIIIIIIIIIIXXIXIIIIIIIIII",
    "IIIIIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIZZIZIIIZZIZIII",
    "IIIIIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIZZIZIII",
    "ZZIZIIIZZIZIIIZZIZIIIIIIIIIIIIIIIIIZZIZIIIIIIIIII"
]

stabilizers.extend(extras)

for i, s in enumerate(stabilizers):
    print(f"{i}: {len(s)} {s}")

with open("stabilizers_49_corrected.txt", "w") as f:
    for s in stabilizers:
        f.write(s + "\n")
