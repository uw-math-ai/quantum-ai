import stim

# Read stabilizers
with open("agent_files/stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

paulis = [stim.PauliString(s) for s in lines]
print(f"Total stabilizers: {len(paulis)}")

# Try to find independent subset using greedy approach
# Remove anticommuting ones
consistent = []
removed = []
for i, p in enumerate(paulis):
    commutes = True
    for j, q in enumerate(consistent):
        if not p.commutes(q):
            commutes = False
            removed.append(i)
            break
    if commutes:
        consistent.append(p)

print(f"Consistent: {len(consistent)}, Removed indices: {removed}")

# Build tableau from consistent set
tab = stim.Tableau.from_stabilizers(consistent, allow_underconstrained=True)
print(f"Tableau qubits: {len(tab)}")

# Use elimination method
c = tab.to_circuit(method='elimination')

# Count gates
cx, cz, h, s, vol = 0, 0, 0, 0, 0
for inst in c:
    nt = len(inst.targets_copy())
    if inst.name == 'CX': 
        cx += nt//2
        vol += nt//2
    elif inst.name == 'CZ': 
        cz += nt//2
        vol += nt//2
    elif inst.name == 'H': 
        h += nt
        vol += nt
    elif inst.name == 'S':
        s += nt
        vol += nt

print(f"CX={cx}, CZ={cz}, H={h}, S={s}, vol={vol}")

# Save circuit
with open("agent_files/candidate2.stim", "w") as f:
    f.write(str(c))
print("Circuit saved")
