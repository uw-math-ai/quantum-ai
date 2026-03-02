import json

with open("arg.json", "r") as f:
    data = json.load(f)

print(json.dumps([str(s) for s in data["stabilizers"]]))
