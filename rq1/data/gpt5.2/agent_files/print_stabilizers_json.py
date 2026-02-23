import json

with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_102.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

print(json.dumps(stabilizers))
