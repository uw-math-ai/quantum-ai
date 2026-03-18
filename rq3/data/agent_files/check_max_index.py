import re

with open("current_baseline.stim", "r") as f:
    text = f.read()

indices = [int(x) for x in re.findall(r'\b\d+\b', text)]
if indices:
    print(f"Max index: {max(indices)}")
else:
    print("No indices found")
