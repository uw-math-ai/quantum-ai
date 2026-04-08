
with open(r"data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", "r") as f:
    stabs = f.read().splitlines()

weights = []
for s in stabs:
    w = sum(1 for c in s if c in "XYZ")
    weights.append(w)

print(f"Number of stabilizers: {len(stabs)}")
print(f"Max weight: {max(weights)}")
print(f"Average weight: {sum(weights)/len(weights)}")
print(f"Weights distribution: {sorted(weights)}")
