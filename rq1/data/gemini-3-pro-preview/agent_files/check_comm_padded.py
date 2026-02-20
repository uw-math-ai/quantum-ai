stabs = []
with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

# Pad all to 180
for i in range(len(stabs)):
    if len(stabs[i]) < 180:
        stabs[i] = stabs[i] + 'I' * (180 - len(stabs[i]))

# Now check S32 vs S144 again
import stim
s32 = stim.PauliString(stabs[32])
s144 = stim.PauliString(stabs[144])
print(f"S32 vs S144: {s32.commutes(s144)}")

# Check if there are other anticommuting pairs after padding
print("Checking all pairs after padding...")
anticomm = []
for i in range(len(stabs)):
    for j in range(i+1, len(stabs)):
        if not stim.PauliString(stabs[i]).commutes(stim.PauliString(stabs[j])):
            anticomm.append((i,j))
            if len(anticomm) > 5: break
    if len(anticomm) > 5: break

print(f"Anticommuting pairs: {anticomm}")
