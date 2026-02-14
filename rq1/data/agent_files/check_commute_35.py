import stim

with open("problem_stabs.txt", "r") as f:
    content = f.read()

stabilizers = [s.strip() for s in content.split(",") if s.strip()]

print(f"Number of stabilizers: {len(stabilizers)}")

for i in range(len(stabilizers)):
    for j in range(i + 1, len(stabilizers)):
        s1 = stim.PauliString(stabilizers[i])
        s2 = stim.PauliString(stabilizers[j])
        if not s1.commutes(s2):
            print(f"Anticommute: {i} and {j}")
            print(f"{i}: {stabilizers[i]}")
            print(f"{j}: {stabilizers[j]}")

print("Done checking.")
