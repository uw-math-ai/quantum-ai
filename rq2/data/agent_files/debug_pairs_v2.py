
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\candidate.stim") as f:
    line = f.readlines()[99]
    parts = line.strip().split()
    args = parts[1:]
    with open("debug_pairs_out.txt", "w") as out:
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                out.write(f"{i//2}: {args[i]} {args[i+1]}\n")
            else:
                out.write(f"DANGLING: {args[i]}\n")
