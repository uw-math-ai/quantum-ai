with open('target_stabilizers_job.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

lengths = {}
for i, line in enumerate(lines):
    l = len(line)
    if l not in lengths:
        lengths[l] = []
    lengths[l].append(i)

print("Lengths distribution:")
for l, indices in lengths.items():
    print(f"Length {l}: {len(indices)} lines")
    if len(indices) < 20:
        print(f"Indices: {indices}")
