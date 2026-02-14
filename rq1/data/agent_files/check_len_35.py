with open("problem_stabs.txt", "r") as f:
    content = f.read()

stabilizers = [s.strip() for s in content.split(",") if s.strip()]

for i, s in enumerate(stabilizers):
    if len(s) != 35:
        print(f"Index {i} has length {len(s)}: {s}")
