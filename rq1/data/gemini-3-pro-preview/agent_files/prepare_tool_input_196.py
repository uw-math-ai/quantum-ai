import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
stabs_path = os.path.join(script_dir, "stabilizers_196.txt")
circuit_path = os.path.join(script_dir, "circuit_196.stim")

with open(stabs_path, "r") as f:
    stabs = [line.strip() for line in f if line.strip()]

with open(circuit_path, "r") as f:
    circuit_str = f.read()

payload = {
    "circuit": circuit_str,
    "stabilizers": stabs
}

print(json.dumps(payload))
