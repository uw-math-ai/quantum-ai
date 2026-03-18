import stim
import collections

c = stim.Circuit.from_file("candidate_perm.stim")
counts = collections.Counter()
for op in c:
    counts[op.name] += len(op.targets_copy()) // (2 if op.name in ["CX", "CZ", "SWAP"] else 1)

print(counts)
