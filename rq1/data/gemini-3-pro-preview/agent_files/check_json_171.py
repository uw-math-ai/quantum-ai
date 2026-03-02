import json

with open("data/gemini-3-pro-preview/agent_files/tool_input_171_v2.json", "r") as f:
    data = json.load(f)

print(f"Circuit length: {len(data['circuit'])}")
print(f"Stabilizers count: {len(data['stabilizers'])}")
print(f"Stabilizers type: {type(data['stabilizers'])}")
print(f"Stabilizer 0 type: {type(data['stabilizers'][0])}")
