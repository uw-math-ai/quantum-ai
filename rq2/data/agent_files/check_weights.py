with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq2\\stabilizers.txt", "r") as f:
    stabs = [line.strip() for line in f if line.strip()]

weights = []
for s in stabs:
    w = sum(1 for c in s if c in 'XYZ')
    weights.append(w)

print(f"Number of stabilizers: {len(weights)}")
if len(weights) > 0:
    print(f"Max weight: {max(weights)}")
    print(f"Average weight: {sum(weights)/len(weights)}")
print(f"Weights: {weights}")
