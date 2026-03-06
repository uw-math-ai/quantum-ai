import stim

with open("stabilizers_54_v2.txt", "r") as f:
    stabilizers = [stim.PauliString(s.strip()) for s in f if s.strip()]

print(f"Checking {len(stabilizers)} stabilizers for commutativity.")

found_anticommuting = False
for i in range(len(stabilizers)):
    for j in range(i+1, len(stabilizers)):
        if not stabilizers[i].commutes(stabilizers[j]):
            print(f"ANTICOMMUTE: {i} and {j}")
            found_anticommuting = True

if not found_anticommuting:
    print("All commute.")
else:
    print("Some anticommute!")
