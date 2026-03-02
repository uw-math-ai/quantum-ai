import stim

s_failed = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZ"

with open("my_stabilizers_135.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

print(f"Total stabilizers in file: {len(stabilizers)}")

if s_failed in stabilizers:
    idx = stabilizers.index(s_failed)
    print(f"Failed stabilizer found at index {idx}")
    
    failed_pauli = stim.PauliString(s_failed)
    
    print("Checking commutativity...")
    for i, s in enumerate(stabilizers):
        p = stim.PauliString(s)
        if not failed_pauli.commutes(p):
            print(f"Anticommutes with index {i}: {s}")
else:
    print("Failed stabilizer NOT found in file.")
    # Maybe try to find close match?
    for i, s in enumerate(stabilizers):
        if s.endswith("ZIZ"):
            print(f"Candidate at {i}: {s}")
