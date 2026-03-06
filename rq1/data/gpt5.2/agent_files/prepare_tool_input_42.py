import json

with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_42.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

with open(r"data\gemini-3-pro-preview\agent_files\circuit_42.stim", "r") as f:
    circuit = f.read().strip()

print(json.dumps({"circuit": circuit, "stabilizers": stabilizers}))
