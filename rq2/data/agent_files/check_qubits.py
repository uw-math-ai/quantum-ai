import stim

with open("stabilizers_d21.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

print(f"Number of stabilizers: {len(stabilizers)}")
print(f"Length of first stabilizer: {len(stabilizers[0])}")

with open("circuit_d21.stim", "r") as f:
    circuit_text = f.read()

circuit = stim.Circuit(circuit_text)
num_qubits = circuit.num_qubits
print(f"Number of qubits in circuit: {num_qubits}")

used_qubits = set()
for instruction in circuit:
    for target in instruction.targets_copy():
        if target.is_qubit_target:
            used_qubits.add(target.value)

print(f"Max used qubit index: {max(used_qubits)}")
print(f"Number of used qubits: {len(used_qubits)}")
