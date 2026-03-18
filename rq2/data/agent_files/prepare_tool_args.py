import json

with open("stabilizers.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

with open("input_circuit.stim", "r") as f:
    circuit = f.read()

data_qubits = list(range(150))
flag_qubits = []

args = {
    "circuit": circuit,
    "stabilizers": stabilizers,
    "data_qubits": data_qubits,
    "flag_qubits": flag_qubits
}

print(json.dumps(args))
