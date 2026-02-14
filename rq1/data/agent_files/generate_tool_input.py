import json
from solve_95_full import stabilizers

with open("circuit_attempt.stim", "r") as f:
    circuit_str = f.read()

tool_input = {
    "circuit": circuit_str,
    "stabilizers": stabilizers
}

# Print as JSON
print(json.dumps(tool_input))
