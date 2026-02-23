import solve_175
import solve_175_new

s_old = solve_175.stabilizers
s_new = solve_175_new.stabilizers

print(f"Old count: {len(s_old)}")
print(f"New count: {len(s_new)}")

# Normalize strings (pad with I to max length)
def normalize(s):
    return s.ljust(175, 'I')

s_old_norm = {normalize(s) for s in s_old}
s_new_norm = {normalize(s) for s in s_new}

print(f"Old normalized count: {len(s_old_norm)}")
print(f"New normalized count: {len(s_new_norm)}")

missing_in_old = s_new_norm - s_old_norm
missing_in_new = s_old_norm - s_new_norm

print(f"Missing in old: {len(missing_in_old)}")
for s in missing_in_old:
    print(f"  {s}")

print(f"Missing in new: {len(missing_in_new)}")
for s in missing_in_new:
    print(f"  {s}")
