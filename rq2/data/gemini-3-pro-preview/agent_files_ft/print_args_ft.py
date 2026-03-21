import json

circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_ft.stim"
stabs_path = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt"
flags_path = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\flag_qubits.txt"

# Read circuit
with open(circuit_path, "r") as f:
    circuit_str = f.read()

# Read stabilizers
with open(stabs_path, "r") as f:
    content = f.read().replace("\n", "").strip()
    stabs = [s.strip() for s in content.split(",") if s.strip()]

# Read flag qubits
with open(flags_path, "r") as f:
    content = f.read().strip()
    if content:
        flag_qubits = [int(x) for x in content.split(",")]
    else:
        flag_qubits = []

# Data qubits
data_qubits = list(range(90))

args = {
    "circuit": circuit_str,
    "stabilizers": stabs,
    "data_qubits": data_qubits,
    "flag_qubits": flag_qubits
}

print(json.dumps(args))
