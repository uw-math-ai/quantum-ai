import stim

with open("circuit_54_v2.stim", "r") as f:
    circuit = stim.Circuit(f.read())

print(f"Num qubits: {circuit.num_qubits}")

# Check usage of qubit 55
usage = []
for i, instr in enumerate(circuit):
    for target in instr.targets_copy():
        if target.value == 55:
            usage.append((i, instr))
            
print(f"Qubit 55 usage: {usage}")
