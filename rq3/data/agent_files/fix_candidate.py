import stim

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate.stim", "r") as f:
    circuit = stim.Circuit(f.read())

new_circuit = stim.Circuit()

# Check first instruction
for i, inst in enumerate(circuit):
    if inst.name == "RX":
        # Replace with H
        new_circuit.append("H", inst.targets_copy())
    else:
        new_circuit.append(inst)

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq3\data\agent_files\candidate_fixed.stim", "w") as f:
    f.write(str(new_circuit))
    
print("Replaced RX with H.")
