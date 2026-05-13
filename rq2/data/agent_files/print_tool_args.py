
import json

with open("candidate.stim", "r") as f:
    circuit = f.read()

with open("ancillas.txt", "r") as f:
    ancillas_str = f.read()
    ancillas = [int(x) for x in ancillas_str.split(",") if x]

from inputs_task import stabilizers, data_qubits

print(json.dumps({
    "circuit": circuit,
    "data_qubits": data_qubits,
    "flag_qubits": ancillas,
    "stabilizers": stabilizers
}))
