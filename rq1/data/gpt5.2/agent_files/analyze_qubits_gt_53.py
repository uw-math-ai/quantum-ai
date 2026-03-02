import stim

with open("circuit_54_v2.stim", "r") as f:
    circuit = stim.Circuit(f.read())

print(f"Num qubits: {circuit.num_qubits}")

# Check usage of qubits > 53
usage = {}
for i, instr in enumerate(circuit):
    for target in instr.targets_copy():
        if target.value > 53:
            if target.value not in usage:
                usage[target.value] = []
            usage[target.value].append(i)
            
print(f"Qubits > 53 usage: {usage}")
