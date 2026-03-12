import re

with open('candidate_graph_state.stim', 'r') as f:
    content = f.read()

# Replace "RX" with "H"
# The view showed "RX 0 1 ...".
# I'll just replace the first occurrence of "RX " with "H ".
# I'll do this carefully.
new_content = re.sub(r'RX\s', 'H ', content, count=1)

with open('candidate_graph_state_fixed.stim', 'w') as f:
    f.write(new_content)
