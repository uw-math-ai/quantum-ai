import json

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_152.stim", "r") as f:
    circuit = f.read()

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers.json", "r") as f:
    stabilizers = json.load(f)

# Note: stabilizers.json contains a list of strings
# The tool expects 'stabilizers' as a list of strings.
# 'circuit' as a string.

input_data = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

# Print the JSON object that can be passed to check_stabilizers_tool
print(json.dumps(input_data))
