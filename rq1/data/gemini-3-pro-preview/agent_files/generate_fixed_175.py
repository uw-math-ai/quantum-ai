
import sys
import os

# Add the directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files'))

# Import generators from analyze_175
# Note: this will execute the print statements in analyze_175, which is fine
from analyze_175 import generators

print(f"Loaded {len(generators)} generators")

fixed_generators = []

def make_gen(pattern, start, length=175):
    if start < 0:
        # Handle negative start (shouldn't happen with correct logic but good for safety)
        prefix = ""
    else:
        prefix = "I" * start
    
    current_len = len(prefix) + len(pattern)
    if current_len > length:
        # Pattern goes beyond length, truncate
        # This shouldn't happen for valid generators
        return (prefix + pattern)[:length]
        
    suffix_len = length - current_len
    suffix = "I" * suffix_len
    return prefix + pattern + suffix

# XXIIIXX groups
# 0-6: start 0
# 7-13: start 10
# 14-20: start 6
# 21-27: start 16
# 28-34: start 2
# 35-41: start 12
# 42-48: start 8
# 49-55: start 18
xx_starts = [0, 10, 6, 16, 2, 12, 8, 18]
for start in xx_starts:
    for i in range(7):
        fixed_generators.append(make_gen("XXIIIXX", start + i*25))

# XIIIIX groups
# 56-62: start 4
# 63-69: start 5
# 70-76: start 14
# 77-83: start 15
xi_starts = [4, 5, 14, 15]
for start in xi_starts:
    for i in range(7):
        fixed_generators.append(make_gen("XIIIIX", start + i*25))

# ZZIIIZZ groups
# 84-90: start 5
# 91-97: start 15
# 98-104: start 1
# 105-111: start 11
# 112-118: start 7
# 119-125: start 17
# 126-132: start 3
# 133-139: start 13
zz_starts = [5, 15, 1, 11, 7, 17, 3, 13]
for start in zz_starts:
    for i in range(7):
        fixed_generators.append(make_gen("ZZIIIZZ", start + i*25))

# ZZ groups
# 140-146: start 0
# 147-153: start 21
# 154-160: start 2
# 161-167: start 23
z_starts = [0, 21, 2, 23]
for start in z_starts:
    for i in range(7):
        fixed_generators.append(make_gen("ZZ", start + i*25))

# Special ones
# 168: 52 XXXXIXIIIX
fixed_generators.append(generators[168])
# 169: 27 XXXXIXIIIX
fixed_generators.append(generators[169])
# 170: 2 XXXXIXIIIX
fixed_generators.append(generators[170])
# 171: 50 ZIIIIIZIII
fixed_generators.append(generators[171])
# 172: 25 ZIIIIIZIII
fixed_generators.append(generators[172])
# 173: 0 ZIIIIIZIII
fixed_generators.append(generators[173])

print(f"Generated {len(fixed_generators)} fixed generators")

# Compare with original
for i, (orig, fixed) in enumerate(zip(generators, fixed_generators)):
    if len(orig) != 175 or orig != fixed:
        print(f"Index {i} changed.")
        # print(f"Orig: {orig} ({len(orig)})")
        # print(f"Fixed: {fixed} ({len(fixed)})")

# Save fixed generators
output_path = os.path.join(os.getcwd(), 'data', 'gemini-3-pro-preview', 'agent_files', 'stabilizers_175_fixed.txt')
with open(output_path, "w") as f:
    for g in fixed_generators:
        f.write(g + "\n")
print(f"Saved to {output_path}")
