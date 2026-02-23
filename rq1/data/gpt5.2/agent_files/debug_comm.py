import stim
import sys

with open("stabilizers_90.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

s11 = stim.PauliString(stabilizers[11])
s82 = stim.PauliString(stabilizers[82])

print(f"s11: {s11}")
print(f"s82: {s82}")

print(f"s11 commutes with s82: {s11.commutes(s82)}")

indices_s11 = [i for i, c in enumerate(str(s11)) if c != "_" and c != "+"]
indices_s82 = [i for i, c in enumerate(str(s82)) if c != "_" and c != "+"]

print(f"s11 non-identity indices: {indices_s11}")
print(f"s82 non-identity indices: {indices_s82}")

intersection = set(indices_s11).intersection(set(indices_s82))
print(f"Intersection: {intersection}")

for i in intersection:
    p1 = str(s11)[i]
    p2 = str(s82)[i]
    print(f"At {i}: {p1} vs {p2}")

