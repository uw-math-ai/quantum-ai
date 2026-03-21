import json
import os

circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim"
stabs_path = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt"

# Read circuit
with open(circuit_path, "r") as f:
    circuit_str = f.read()

# Read stabilizers
with open(stabs_path, "r") as f:
    content = f.read().replace("\n", "").strip()
    stabs = [s.strip() for s in content.split(",") if s.strip()]

# Data qubits
data_qubits = list(range(90))
flag_qubits = []

args = {
    "circuit": circuit_str,
    "stabilizers": stabs,
    "data_qubits": data_qubits,
    "flag_qubits": flag_qubits
}

print(json.dumps(args))
