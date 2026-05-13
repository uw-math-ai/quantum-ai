
import json

with open("candidate.stim", "r") as f:
    circuit_str = f.read()

print(json.dumps(circuit_str))
