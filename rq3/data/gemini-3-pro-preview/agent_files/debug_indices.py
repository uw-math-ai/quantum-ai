s44 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
s128 = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ"

def get_indices(s):
    indices = []
    for i, c in enumerate(s):
        if c != 'I':
            indices.append((i, c))
    return indices

print(f"S44: {get_indices(s44)}")
print(f"S128: {get_indices(s128)}")

# Check overlap
# Wait, s128 has 'ZZ' at the end. s44 has 'XX...XX' somewhere in the middle.
# They shouldn't overlap at all.
# Why did stim say they anticommute?

# Let me re-read the error message from my first attempt.
# stabilizers[44] = +...XX...XX...
# stabilizers[128] = +...ZZ...

# Wait, maybe the indices in the error message refer to the list I passed, which might be different from the prompt?
# I copied the list directly.

# Maybe I misread the error message or the file content.
# Let's check the length of the list.
