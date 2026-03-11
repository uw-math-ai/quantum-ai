import stim

# Read stabilizers
with open("agent_files/stabilizers.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]

paulis = [stim.PauliString(s) for s in lines]
n = len(paulis)

# More thorough anticommuting analysis
anticommute_pairs = []
for i in range(n):
    for j in range(i+1, n):
        if not paulis[i].commutes(paulis[j]):
            anticommute_pairs.append((i, j))

print(f"All anticommuting pairs ({len(anticommute_pairs)}):")
for pair in anticommute_pairs:
    print(f"  {pair[0]} vs {pair[1]}")

# Try to find maximum consistent subset
# Greedy approach with different ordering
# First, exclude all problematic stabilizers
problematic = {35, 37, 111, 112, 149, 150, 153, 162, 163, 165, 166}
non_problematic = [p for i, p in enumerate(paulis) if i not in problematic]
print(f"\nAfter removing all 11 problematic: {len(non_problematic)} stabilizers")

# Check if consistent
still_anticommute = False
for i in range(len(non_problematic)):
    for j in range(i+1, len(non_problematic)):
        if not non_problematic[i].commutes(non_problematic[j]):
            still_anticommute = True
            print(f"Still anticommuting!")
            break
    if still_anticommute:
        break

if not still_anticommute:
    print("Consistent set found!")
    tab = stim.Tableau.from_stabilizers(non_problematic, allow_underconstrained=True)
    print(f"Tableau: {len(tab)} qubits")
    
    c = tab.to_circuit(method='elimination')
    
    cx = 0
    for inst in c:
        if inst.name == 'CX': cx += len(inst.targets_copy())//2
    print(f"CX count: {cx}")
    
    with open("agent_files/candidate4.stim", "w") as f:
        f.write(str(c))
