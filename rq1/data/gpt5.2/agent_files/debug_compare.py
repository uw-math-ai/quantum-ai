
bad_stab = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII"
print(f"Bad stab length: {len(bad_stab)}")

with open("stabilizers_133.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

found = False
for l in lines:
    if l == bad_stab:
        found = True
        break
    if l.endswith("XXXXIIIIIIIIIIIIIIIIIIIII") and len(l) == len(bad_stab):
        print(f"Found similar ending: {l}")
        # Compare char by char
        for i, (c1, c2) in enumerate(zip(l, bad_stab)):
            if c1 != c2:
                print(f"Diff at {i}: file={c1}, bad={c2}")

print(f"Found exact: {found}")
