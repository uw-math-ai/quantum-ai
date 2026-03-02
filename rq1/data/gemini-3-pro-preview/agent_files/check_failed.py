failed_stabs = [
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIIIIII"
]

for s in failed_stabs:
    print(f"Length: {len(s)}")
    # Find indices of non-I
    indices = []
    for i, c in enumerate(s):
        if c != 'I':
            indices.append((i, c))
    print(f"Non-I indices: {indices}")
