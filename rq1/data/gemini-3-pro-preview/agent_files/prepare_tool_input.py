import solve_135
import json
import os

# Get stabilizers from the solver script
stabilizers = solve_135.stabilizers

# Read the circuit file
base_dir = r"C:\Users\anpaz\Repos\quantum-ai\rq1"
circ_path = os.path.join(base_dir, "circuit_clean_135.stim")

with open(circ_path, "r") as f:
    circuit = f.read()

output = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

with open(os.path.join(base_dir, "tool_input.json"), "w") as f:
    json.dump(output, f)

print(f"Tool input written to {os.path.join(base_dir, 'tool_input.json')}")
