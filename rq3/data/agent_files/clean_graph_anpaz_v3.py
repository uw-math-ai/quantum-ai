import stim

try:
    circuit = stim.Circuit.from_file("candidate_graph.stim")
except Exception as e:
    print(f"Error reading circuit: {e}")
    exit(1)

new_circuit = stim.Circuit()

for instruction in circuit:
    if instruction.name == "RX":
        # Replace RX with H
        targets = [t.value for t in instruction.targets_copy()]
        new_circuit.append("H", targets)
    elif instruction.name == "TICK":
        new_circuit.append("TICK")
    else:
        new_circuit.append(instruction)

with open("candidate_graph_clean.stim", "w") as f:
    f.write(str(new_circuit))
    
print("Cleaned circuit saved to candidate_graph_clean.stim")
