import stim
with open("candidate_final.stim", "r") as f:
    content = f.read()

print(content)

# Get ancillas
c = stim.Circuit(content)
# Ancillas are 49+
max_q = 0
for op in c.flattened():
    for t in op.targets_copy():
        if t.is_qubit_target:
            max_q = max(max_q, t.value)

ancillas = list(range(49, max_q+1))
print(f"# ANCILLAS: {ancillas}")
