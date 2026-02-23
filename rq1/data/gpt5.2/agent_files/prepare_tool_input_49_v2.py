import json

with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_49_task.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

try:
    with open("circuit_49_generated.stim", "r") as f:
        circuit = f.read()
except FileNotFoundError:
    print("Circuit file not found.")
    circuit = ""

print(json.dumps({"circuit": circuit, "stabilizers": stabilizers}))
