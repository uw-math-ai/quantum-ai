import json

with open('circuit_161_subset.stim', 'r') as f:
    circuit = f.read()

with open('stabilizers_161_fixed.txt', 'r') as f:
    stabilizers = [line.strip() for line in f if line.strip()]

output = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

with open('tool_input_161.json', 'w') as f:
    json.dump(output, f)

print("Saved tool input to tool_input_161.json")
