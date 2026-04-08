
import json

with open("candidate.stim", "r") as f:
    circuit = f.read()

with open("ancillas.txt", "r") as f:
    ancillas_str = f.read()
    ancillas = [int(x) for x in ancillas_str.split(",") if x]

print("Ancillas count:", len(ancillas))
print("First:", ancillas[0], "Last:", ancillas[-1])
