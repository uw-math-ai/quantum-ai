import re

with open("candidate.stim", "r") as f:
    content = f.read()

# Check for 54 and 55 usage
for q in [54, 55]:
    # Regex to find whole word q
    if re.search(r'\b' + str(q) + r'\b', content):
        print(f"Qubit {q} found in:")
        for line in content.splitlines():
            if re.search(r'\b' + str(q) + r'\b', line):
                print(line)
