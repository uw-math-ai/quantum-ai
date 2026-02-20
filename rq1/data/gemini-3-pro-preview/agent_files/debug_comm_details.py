import stim

# Reconstruct stabs locally for calculation
def get_stabs():
    # The list is in the file
    with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
        return [line.strip() for line in f if line.strip()]

stabs = get_stabs()

s32 = stim.PauliString(stabs[32])
s144 = stim.PauliString(stabs[144])

print(f"S32:  {s32}")
print(f"S144: {s144}")
print(f"Commutes: {s32.commutes(s144)}")

# Check overlap at 160-163
# S32 is XZZX at 160-163?
# Let's find where S32 is non-identity
for i in range(180):
    if stabs[32][i] != 'I':
        print(f"S32 index {i}: {stabs[32][i]}")

# Check S144 at these indices
for i in range(180):
    if stabs[32][i] != 'I':
        print(f"S144 index {i}: {stabs[144][i]}")

