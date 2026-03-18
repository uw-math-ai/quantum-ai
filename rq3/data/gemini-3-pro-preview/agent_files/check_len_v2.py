with open("target_stabilizers_rq3_new_v5.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

for i, l in enumerate(lines):
    if len(l) != 120:
        print(f"Line {i}: length {len(l)}")
        print(l)
