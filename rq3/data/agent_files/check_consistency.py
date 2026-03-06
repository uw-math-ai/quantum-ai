import stim

with open("real_stabilizers.txt", "r") as f:
    lines = [l.strip().replace(',', '') for l in f if l.strip()]

print(f"Number of lines: {len(lines)}")
lengths = [len(l) for l in lines]
print(f"Lengths: {lengths}")
print(f"Max length: {max(lengths)}")
print(f"Min length: {min(lengths)}")

# Check if they are consistent assuming padding
max_len = max(lengths)
padded_lines = []
for l in lines:
    padded_lines.append(l + "_" * (max_len - len(l))) # use _ to visualize, but for stim need I

stim_lines = [l + "I" * (max_len - len(l)) for l in lines]

try:
    t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stim_lines])
    print("Stabilizers are consistent!")
except Exception as e:
    print(f"Stabilizers are INCONSISTENT: {e}")

# Check specific pair 0 and 17 (index 18?)
# Actually line 17 in file is index 16.
# Error said "stabilizers[17]". This is index 17 (18th stabilizer).
if len(lines) > 17:
    s0 = stim.PauliString(stim_lines[0])
    s17 = stim.PauliString(stim_lines[17])
    print(f"S0:  {s0}")
    print(f"S17: {s17}")
    print(f"Commute? {s0.commutes(s17)}")
