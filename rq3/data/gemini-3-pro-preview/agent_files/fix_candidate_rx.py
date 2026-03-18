import re

with open("candidate.stim", "r") as f:
    content = f.read()

# Replace RX with H
# RX is likely at the beginning of the line
new_content = re.sub(r"^RX\b", "H", content)
# Also check if RX appears elsewhere (unlikely for graph state init)
# But just in case, graph state logic is: Init + -> CZ -> Local Cliffords
# So RX is likely only for init.

with open("candidate.stim", "w") as f:
    f.write(new_content)

print("Replaced RX with H in candidate.stim")
