import stim

# Read stabilizers - but exclude the last 9 stabilizers which seem to cause issues
with open("agent_files/stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

paulis = [stim.PauliString(s) for s in lines]
n = len(paulis)
print(f"Total stabilizers: {n}")

# Check which stabilizers are involved in anticommuting pairs
anticommute_involved = set()
for i in range(n):
    for j in range(i+1, n):
        if not paulis[i].commutes(paulis[j]):
            anticommute_involved.add(i)
            anticommute_involved.add(j)

print(f"Stabilizers involved in anticommuting: {sorted(anticommute_involved)}")

# Try removing stabilizer 153 which appears in most conflicts
to_remove = {153}
consistent = [p for i, p in enumerate(paulis) if i not in to_remove]
print(f"After removing {to_remove}: {len(consistent)} stabilizers")

# Check if now consistent
has_anticommute = False
for i in range(len(consistent)):
    for j in range(i+1, len(consistent)):
        if not consistent[i].commutes(consistent[j]):
            has_anticommute = True
            print(f"Still anticommuting: {i} vs {j}")
            break
    if has_anticommute:
        break

if not has_anticommute:
    print("All stabilizers now commute!")
    
    # Build tableau
    tab = stim.Tableau.from_stabilizers(consistent, allow_underconstrained=True)
    print(f"Tableau qubits: {len(tab)}")
    
    # Generate circuit
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
    
    with open("agent_files/candidate3.stim", "w") as f:
        f.write(str(c))
    print("Circuit saved to candidate3.stim")
