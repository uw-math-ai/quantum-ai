
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\candidate.stim") as f:
    line = f.readlines()[99]
    parts = line.strip().split()
    args = parts[1:]
    print(f"Total args: {len(args)}")
    for i in range(0, len(args), 2):
        if i+1 < len(args):
            # print(f"{i//2}: {args[i]} {args[i+1]}")
            pass
        else:
            print(f"DANGLING at end: {args[i]}")
