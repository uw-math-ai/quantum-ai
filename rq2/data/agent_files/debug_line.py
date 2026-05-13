
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\candidate.stim") as f:
    lines = f.readlines()
    if len(lines) > 99:
        print(lines[99])
