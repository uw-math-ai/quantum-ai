import json

def load_file(path):
    with open(path, 'r') as f:
        return f.read().strip()

circuit = load_file(r"data\gemini-3-pro-preview\agent_files_ft\circuit.stim")
stabilizers_str = load_file(r"data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt")
stabilizers = [s.strip() for s in stabilizers_str.split(',')]

# Data qubits are 0 to 104
data_qubits = list(range(105))
flag_qubits = []

args = {
    "circuit": circuit,
    "stabilizers": stabilizers,
    "data_qubits": data_qubits,
    "flag_qubits": flag_qubits
}

print(json.dumps(args))
