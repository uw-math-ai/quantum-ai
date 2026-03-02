import json

with open(r"data\gemini-3-pro-preview\agent_files\circuit_102_clean.stim", "r") as f:
    circuit_text = f.read()

print(json.dumps(circuit_text))
