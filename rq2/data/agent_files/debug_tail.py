
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\candidate.stim") as f:
    lines = f.readlines()
    if len(lines) > 99:
        line = lines[99]
        parts = line.strip().split()
        print(parts[-10:])
