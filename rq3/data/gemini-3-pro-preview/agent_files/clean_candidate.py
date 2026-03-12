import sys

with open("candidate.stim", "r") as f:
    lines = f.readlines()

with open("candidate_clean.stim", "w") as f:
    for line in lines:
        if "TICK" in line:
            continue
        f.write(line)
