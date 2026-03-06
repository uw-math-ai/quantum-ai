def analyze(s, name):
    first_z = s.find('Z')
    last_z = s.rfind('Z')
    print(f"{name}: len={len(s)}, first_z={first_z}, last_z={last_z}")
    # Print the block containing Zs
    if first_z != -1:
        print(f"  Block: {s[first_z:last_z+1]}")

with open("stabilizers_186.txt", "r") as f:
    lines = [line.strip() for line in f]

analyze(lines[103], "S103")
analyze(lines[104], "S104")
analyze(lines[105], "S105")
analyze(lines[106], "S106")
