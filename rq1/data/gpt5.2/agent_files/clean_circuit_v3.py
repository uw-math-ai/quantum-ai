import stim

with open("circuit_54_v2.stim", "r") as f:
    circuit = stim.Circuit(f.read())

print(f"Original length: {len(circuit)}")

# Remove last instruction (H 55 55)
new_circuit = circuit.copy()
new_circuit.pop()

print(f"New length: {len(new_circuit)}")

# Verify no qubits > 53 are used
for instr in new_circuit:
    for target in instr.targets_copy():
        if target.value > 53:
            print(f"WARNING: Qubit {target.value} used in instruction {instr}")

with open("circuit_54_v3.stim", "w") as f:
    f.write(str(new_circuit))
    
print("Saved circuit_54_v3.stim")
