with open('attempt_2.stim', 'r') as f:
    lines = f.readlines()

with open('candidate_opt.stim', 'w') as f:
    start = False
    for line in lines:
        if line.strip().startswith("H") or line.strip().startswith("CX") or line.strip().startswith("CZ"):
            start = True
        if start:
            f.write(line)
