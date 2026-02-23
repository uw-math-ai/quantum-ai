import json

with open("data/gemini-3-pro-preview/agent_files/circuit_171.stim", "r") as f:
    circuit = f.read().strip()

with open("data/gemini-3-pro-preview/agent_files/stabilizers_171.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

output = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

print(json.dumps(output))
