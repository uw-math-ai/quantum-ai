import stim

# Read stabilizers
with open("agent_files/stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

paulis = [stim.PauliString(s) for s in lines]
print(f"Total stabilizers: {len(paulis)}")
print(f"Stabilizer length: {len(lines[0]) if lines else 0}")

# Try to find consistent subset
consistent = []
for i, p in enumerate(paulis):
    commutes = True
    for j, q in enumerate(consistent):
        if p.commutes(q) == False:
            commutes = False
            print(f"Stabilizer {i} anticommutes with existing set")
            break
    if commutes:
        consistent.append(p)

print(f"Consistent subset size: {len(consistent)}")

# Build tableau from consistent set
tab = stim.Tableau.from_stabilizers(consistent, allow_underconstrained=True)
print(f"Tableau qubits: {len(tab)}")

# Generate with graph_state
c = tab.to_circuit(method='graph_state')

# Count gates
cx, cz, h, vol = 0, 0, 0, 0
for inst in c:
    if inst.name == 'CX': cx += len(inst.targets_copy())//2
    elif inst.name == 'CZ': cz += len(inst.targets_copy())//2
    elif inst.name == 'H': h += len(inst.targets_copy())
    vol += len(inst.targets_copy()) if inst.name in ['H','S','SQRT_X'] else len(inst.targets_copy())//2 if inst.name in ['CX','CZ','CY'] else 0

print(f"CX={cx}, CZ={cz}, H={h}, vol(2q+1q)={vol}")

# Save circuit
with open("agent_files/candidate1.stim", "w") as f:
    f.write(str(c))
print("Circuit saved")
