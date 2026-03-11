import stim

# Read stabilizers
with open("agent_files/stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

paulis = [stim.PauliString(s) for s in lines]
print(f"Total stabilizers: {len(paulis)}")

# Build tableau
tab = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
print(f"Tableau qubits: {len(tab)}")

# Generate with graph_state
c = tab.to_circuit(method='graph_state')

# Count gates
cx, cz, h = 0, 0, 0
for inst in c:
    if inst.name == 'CX': cx += len(inst.targets_copy())//2
    elif inst.name == 'CZ': cz += len(inst.targets_copy())//2
    elif inst.name == 'H': h += len(inst.targets_copy())

print(f"CX={cx}, CZ={cz}, H={h}")

# Save circuit
with open("agent_files/candidate1.stim", "w") as f:
    f.write(str(c))
print("Circuit saved to agent_files/candidate1.stim")
