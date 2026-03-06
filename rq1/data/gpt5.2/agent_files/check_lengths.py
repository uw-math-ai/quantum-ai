from solve_175 import stabilizers

for i, s in enumerate(stabilizers):
    if len(s) != 175:
        print(f"Stabilizer {i} has length {len(s)}")
