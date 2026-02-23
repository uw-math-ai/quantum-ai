import json

# Read circuit
with open("data/gemini-3-pro-preview/agent_files/circuit_133.stim", "r") as f:
    lines = f.readlines()
    if lines and "Success" in lines[0]:
        lines = lines[1:]
    circuit = "".join(lines).strip()

# Read stabilizers
with open("data/gemini-3-pro-preview/agent_files/stabilizers_133_correct.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

print("---CIRCUIT_START---")
print(circuit)
print("---CIRCUIT_END---")
print("---STABILIZERS_START---")
print(json.dumps(stabilizers))
print("---STABILIZERS_END---")
