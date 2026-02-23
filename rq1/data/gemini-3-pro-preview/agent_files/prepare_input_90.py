import json

with open("data/gemini-3-pro-preview/agent_files/stabilizers_90.txt", "r") as f:
    stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]

with open("data/gemini-3-pro-preview/agent_files/circuit_90.stim", "r") as f:
    circuit = f.read()

payload = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

# Write to a file so I can cat it
with open("data/gemini-3-pro-preview/agent_files/tool_input_90.json", "w") as f:
    json.dump(payload, f)

print("Written to tool_input_90.json")
