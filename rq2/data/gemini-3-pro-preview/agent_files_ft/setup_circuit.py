import sys
import subprocess
import stim

# Inputs
input_circuit_str = """CX 1 0 0 1 1 0
H 0
CX 0 2 0 3 0 8
H 1
CX 1 0 2 1 1 2 2 1 2 1 3 2 2 3 3 2 3 2 3 4 3 5 7 6 6 7 7 6 6 7 8 6 8 7"""

stabilizers = [
    "XXXXXXIII", "XXXIIIXXX", 
    "ZZIIIIIII", "ZIZIIIIII", 
    "IIIZZIIII", "IIIZIZIII", 
    "IIIIIIZZI", "IIIIIIZIZ"
]
distance = 3
data_qubits = list(range(9))

def format_circuit(c_str):
    # Normalize the input string to valid Stim format
    lines = c_str.strip().split('\n')
    formatted = []
    for line in lines:
        parts = line.split()
        if not parts: continue
        gate = parts[0]
        targets = [int(x) for x in parts[1:]]
        # Group targets if necessary, but Stim handles "CX 1 0 0 1" fine
        # Just ensure spaces
        formatted.append(f"{gate} {' '.join(str(t) for t in targets)}")
    return "\n".join(formatted)

base_circuit = format_circuit(input_circuit_str)
print("Base Circuit:")
print(base_circuit)
