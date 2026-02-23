import json

with open("my_circuit_135.stim", "r") as f:
    circuit_str = f.read()

with open("my_stabilizers_135.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

print("CIRCUIT_START")
print(circuit_str)
print("CIRCUIT_END")

print("STABILIZERS_START")
print(json.dumps(stabilizers))
print("STABILIZERS_END")
