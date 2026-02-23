import solve_175_new
stabs = solve_175_new.stabilizers
print(f"Total stabilizers: {len(stabs)}")
for i, s in enumerate(stabs):
    if len(s) != 175:
        print(f"Stabilizer {i} has length {len(s)}")
