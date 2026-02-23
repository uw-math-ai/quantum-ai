import stim

with open("circuit_54_graph.stim", "r") as f:
    circuit = stim.Circuit(f.read())

# Filter instructions to remove > 53
new_circuit = stim.Circuit()
for instr in circuit:
    targets = instr.targets_copy()
    new_targets = [t for t in targets if t.value <= 53]
    if new_targets:
        if len(new_targets) == len(targets):
            new_circuit.append(instr)
        else:
            # Reconstruct instruction with filtered targets
            # Check if gate supports multiple targets
            # Most gates do.
            # CZ requires pairs. If we remove one, we must remove its partner?
            # But wait, my check said NO interactions between >53 and <=53.
            # So if >53 is present, its partner must also be >53.
            # So we can just remove >53 targets safely.
            new_circuit.append(instr.name, new_targets)

with open("circuit_54_graph_clean.stim", "w") as f:
    f.write(str(new_circuit))
    
print("Saved circuit_54_graph_clean.stim")
