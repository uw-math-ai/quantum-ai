import json

with open("stabilizers_72_fixed.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

with open("circuit_72_solution.stim", "r") as f:
    circuit = f.read()

data = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

print(json.dumps(data))
