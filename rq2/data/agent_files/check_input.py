import stim
import sys

# Load circuit
with open("circuit_rq2.stim", "r") as f:
    circuit_str = f.read()

# Load stabilizers
with open("stabilizers_rq2.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

# Data qubits 0 to 124
data_qubits = list(range(125))
flag_qubits = []

# Prepare arguments for validate_circuit
# (This is just for my local check or to verify the parser, actual validation happens via the tool)
print(f"Loaded {len(stabilizers)} stabilizers.")
print(f"Loaded circuit of length {len(circuit_str)} chars.")
