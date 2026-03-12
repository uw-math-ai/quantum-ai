import re

with open("baseline.stim", "r") as f:
    text = f.read()

numbers = [int(s) for s in re.findall(r'\b\d+\b', text)]
if numbers:
    print(max(numbers))
else:
    print("No numbers found")
