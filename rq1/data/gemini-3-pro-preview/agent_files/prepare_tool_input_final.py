import json
import solve_105_new

stabilizers = solve_105_new.stabilizers
with open(r"data/gemini-3-pro-preview/agent_files/circuit_105.stim", "r") as f:
    circuit = f.read()

input_data = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

print(json.dumps(input_data))
