import stim

def load_file(path):
    with open(path, 'r') as f:
        return f.read().strip()

with open(r"data\gemini-3-pro-preview\agent_files_ft\circuit.stim", 'r') as f:
    circuit_str = f.read()

with open(r"data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt", 'r') as f:
    stabilizers_str = f.read()

stabilizers = [s.strip() for s in stabilizers_str.split(',')]
# stim.Circuit(circuit_str)
circuit = stim.Circuit(circuit_str)

# Identify data qubits from stabilizers
# The stabilizers are length N strings. The index in the string is the qubit index.
data_qubits = set()
for s in stabilizers:
    for i, char in enumerate(s):
        if char not in ['I', '_']:
            data_qubits.add(i)

# Identify all qubits in circuit
all_qubits = set()
for instruction in circuit:
    for target in instruction.targets_copy():
        if target.is_qubit_target:
            all_qubits.add(target.value)

ancilla_qubits = all_qubits - data_qubits

print(f"Data qubits count: {len(data_qubits)}")
print(f"Data qubits: {sorted(list(data_qubits))}")
print(f"Ancilla qubits count: {len(ancilla_qubits)}")
print(f"Ancilla qubits: {sorted(list(ancilla_qubits))}")
