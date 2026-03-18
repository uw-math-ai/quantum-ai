import re

with open("data/gemini-3-pro-preview/agent_files/candidate_graph_state.stim", "r") as f:
    content = f.read()

# Remove TICK lines
content = re.sub(r"TICK.*\n", "", content)

# Replace RX with H at the start (assuming clean |0> state)
# RX resets to X basis. H on |0> prepares X basis.
content = content.replace("RX", "H")

# Write to candidate.stim
with open("candidate.stim", "w") as f:
    f.write(content)
