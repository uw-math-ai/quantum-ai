stabs = []
with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
    stabs = [line.strip() for line in f if line.strip()]

print(f"S32 length: {len(stabs[32])}")
print(f"S144 length: {len(stabs[144])}")

for i in range(len(stabs[32])):
    if stabs[32][i] != 'I':
        print(f"S32[{i}] = {stabs[32][i]}")
        print(f"S144[{i}] = {stabs[144][i]}")

