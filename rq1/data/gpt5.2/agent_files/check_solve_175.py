import solve_175
import stim

try:
    p1 = stim.PauliString("IX")
    p2 = stim.PauliString("Z")
    print(f"Created mismatched lengths: {len(p1)} vs {len(p2)}")
except Exception as e:
    print(f"Creation failed: {e}")

stabs = solve_175.stabilizers
print(f"Total stabilizers: {len(stabs)}")

# Check lengths
for i, s in enumerate(stabs):
    if len(s) != 175:
        print(f"Stabilizer {i} has length {len(s)}")

print(f"Stabilizer 100 in solve_175.py: {stabs[100]}")
pauli_strings = [stim.PauliString(s) for s in stabs]
for i in range(len(pauli_strings)):
    for j in range(i + 1, len(pauli_strings)):
        if not pauli_strings[i].commutes(pauli_strings[j]):
            print(f"Anticommuting pair: {i} and {j}")
            print(f"  {i}: {stabs[i]}")
            print(f"  {j}: {stabs[j]}")
            break
