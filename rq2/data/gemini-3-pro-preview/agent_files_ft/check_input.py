import sys
import os

# Read stabilizers
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers_d10.txt', 'r') as f:
    content = f.read().strip()
    # It seems to be a comma separated list of strings
    stabilizers = [s.strip() for s in content.split(',')]
    
if stabilizers:
    print(f"Number of stabilizers: {len(stabilizers)}")
    print(f"Stabilizer length: {len(stabilizers[0])}")
else:
    print("No stabilizers found")

# Read circuit
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_d10.stim', 'r') as f:
    circuit_str = f.read()
    
# Find max qubit
max_q = 0
for line in circuit_str.split('\n'):
    parts = line.strip().split()
    for p in parts:
        try:
            val = int(p)
            if val > max_q:
                max_q = val
        except ValueError:
            pass
print(f"Max qubit index: {max_q}")

# We assume data qubits are 0 to max_q
data_qubits = list(range(max_q + 1))
flag_qubits = []

print(f"Data qubits: {len(data_qubits)}")
