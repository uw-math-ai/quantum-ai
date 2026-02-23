import json

with open("stabilizers_186.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

if len(lines[105]) == 184:
    lines[105] = "II" + lines[105]

print(json.dumps(lines))
