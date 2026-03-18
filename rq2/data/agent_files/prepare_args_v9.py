
import json

def get_stabilizers():
    with open(r"data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt", "r") as f:
        content = f.read().strip()
    # Split by comma and strip whitespace, removing newlines
    content = content.replace('\n', '')
    stabs = [s.strip() for s in content.split(',') if s.strip()]
    return stabs

def get_circuit():
    with open(r"data/gemini-3-pro-preview/agent_files_ft/input_circuit.stim", "r") as f:
        return f.read()

stabs = get_stabilizers()
circuit = get_circuit()
# Data qubits are 0 to 118.
data_qubits = list(range(119))
flag_qubits = []

output = {
    "circuit": circuit,
    "stabilizers": stabs,
    "data_qubits": data_qubits,
    "flag_qubits": flag_qubits
}

print(json.dumps(output))
