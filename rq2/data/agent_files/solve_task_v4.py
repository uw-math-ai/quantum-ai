
import inputs_task_v2
import stim

circuit_str = inputs_task_v2.circuit
stabilizers = inputs_task_v2.stabilizers

# Parse circuit to find used qubits
c = stim.Circuit(circuit_str)
used_qubits = set()
for inst in c:
    for t in inst.targets_copy():
        if hasattr(t, "value"):
            used_qubits.add(t.value)

max_qubit = max(used_qubits)
print(f"Max qubit index: {max_qubit}")
print(f"Stabilizer length: {len(stabilizers[0])}")

data_qubits = list(range(max_qubit + 1))
flag_qubits = []

print(f"Data qubits: {data_qubits}")
print(f"Flag qubits: {flag_qubits}")
