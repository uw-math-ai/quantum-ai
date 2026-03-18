import sys

with open("candidate.stim", "r") as f:
    content = f.read()

content = content.replace("RX ", "H ")

with open("candidate_fixed.stim", "w") as f:
    f.write(content)
