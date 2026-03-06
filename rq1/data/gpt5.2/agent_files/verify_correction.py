import stim

# Stabilizers
with open("stabilizers_54_v2.txt", "r") as f:
    stabilizers = [stim.PauliString(s.strip()) for s in f if s.strip()]

# Correction operator
P = stim.PauliString("ZIIZIIZIIIIIIIIIIIIIIIIIIIIIIZIIIIIIIIIIIIIIIIIIIIIIII")

# Check commutation with S_14 (index 14)
s14 = stabilizers[14]
print(f"S_14: {s14}")
print(f"Correction P: {P}")

if P.commutes(s14):
    print("Commutes with S_14")
else:
    print("ANTICOMMUTES with S_14!")

# Check commutation with all
for i, s in enumerate(stabilizers):
    if not P.commutes(s):
        print(f"Anticommutes with S_{i}")
