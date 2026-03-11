import sys
import stim

# 1. Read
with open("candidate_v2.stim") as f:
    content = f.read()

# 2. Fix RX
content = content.replace("RX ", "H ")

# 3. Write
with open("candidate_final.stim", "w") as f:
    f.write(content)
